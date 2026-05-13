"""Loan workflow: borrowing books, returning them, attaching fines.

This module owns the *business* invariants that surround a
:class:`~app.models.loan.Loan`. The route layer should call into this
module rather than touching the ORM directly -- it keeps view
functions thin and ensures rules like "decrement ``available_copies``
on borrow" cannot be accidentally bypassed.

All public functions raise :class:`BorrowError` (a subclass of
:class:`Exception`) for predictable, user-facing validation failures.
Unexpected database errors are allowed to propagate.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from flask import current_app

from ..extensions import db
from ..models.book import Book
from ..models.fine import Fine
from ..models.loan import Loan
from ..models.user import User
from .fine_service import calculate_fine


class BorrowError(Exception):
    """Raised when a borrow request cannot be satisfied.

    The exception's message is safe to surface to end users via a flash
    message -- it intentionally does not include any internal details.
    """


def borrow_book(user: User, book: Book) -> Loan:
    """Create a loan for ``user`` and decrement the book's availability.

    Parameters
    ----------
    user:
        The patron who wants to borrow the book.
    book:
        The catalogue entry being borrowed.

    Returns
    -------
    Loan
        The newly persisted loan row, with ``id`` populated.

    Raises
    ------
    BorrowError
        If ``book`` is not currently available for borrowing (either
        flagged as lost or with no remaining copies on the shelf).
    """
    if not book.is_available:
        raise BorrowError("This book is not available for borrowing.")

    loan_days: int = current_app.config["LOAN_DAYS"]
    loan = Loan(
        user_id=user.id,
        book_id=book.id,
        borrowed_at=datetime.utcnow(),
        due_at=Loan.default_due_date(loan_days),
    )
    # Decrement first so any race that *would* happen against a parallel
    # transaction is surfaced via the unique check on ``available_copies``
    # instead of double-issuing the same physical copy.
    book.available_copies -= 1
    db.session.add(loan)
    db.session.commit()
    return loan


def return_book(loan: Loan) -> Optional[Fine]:
    """Mark ``loan`` as returned, restock the book and fine if overdue.

    Parameters
    ----------
    loan:
        The loan to close. May be already-returned (in which case any
        previously-attached fine is returned and no further side
        effects occur).

    Returns
    -------
    Fine | None
        The fine that was just created, or ``None`` if the return was
        on time. For an already-returned loan, returns the existing
        fine (or ``None`` if there was none).
    """
    if loan.returned_at is not None:
        return loan.fine

    loan.returned_at = datetime.utcnow()
    loan.book.available_copies += 1

    raw_days = (loan.returned_at - loan.due_at).days
    days_overdue = max(0, raw_days - 1)

    fine: Optional[Fine] = None
    if days_overdue > 0:
        amount = calculate_fine(days_overdue)
        fine = Fine(loan_id=loan.id, amount=amount, paid=False)
        db.session.add(fine)

    db.session.commit()
    return fine
