"""Loan ORM model.

A :class:`Loan` records that a single :class:`~app.models.user.User`
borrowed a single :class:`~app.models.book.Book` at a point in time.
While ``returned_at`` is ``None`` the loan is *active*; once the patron
brings the book back the service layer stamps ``returned_at`` and, if
the return is late, attaches a :class:`~app.models.fine.Fine`.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

from ..extensions import db


class Loan(db.Model):
    """A single borrow event linking a user and a book."""

    __tablename__ = "loans"
    __allow_unmapped__ = True

    # ------------------------------------------------------------------
    # Columns
    # ------------------------------------------------------------------
    id: int = db.Column(db.Integer, primary_key=True)
    user_id: int = db.Column(
        db.Integer, db.ForeignKey("users.id"), nullable=False
    )
    book_id: int = db.Column(
        db.Integer, db.ForeignKey("books.id"), nullable=False
    )
    borrowed_at: datetime = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow
    )
    due_at: datetime = db.Column(db.DateTime, nullable=False)
    #: ``None`` while the loan is still active.
    returned_at: Optional[datetime] = db.Column(db.DateTime, nullable=True)

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------
    user = db.relationship("User", back_populates="loans")
    book = db.relationship("Book", back_populates="loans")
    #: Optional fine attached when a late return is processed.
    fine = db.relationship("Fine", back_populates="loan", uselist=False)

    # ------------------------------------------------------------------
    # Domain helpers
    # ------------------------------------------------------------------
    def is_overdue(self, now: Optional[datetime] = None) -> bool:
        """Return ``True`` if this loan is past its due date.

        For an *active* loan we compare the due date with ``now`` (which
        defaults to the current UTC time). For a *returned* loan we
        instead compare with the actual return timestamp -- a book that
        was technically late but has already been returned is still
        considered overdue.
        """
        now = now or datetime.utcnow()
        reference = self.returned_at or now
        return reference > self.due_at

    def days_overdue(self, now: Optional[datetime] = None) -> int:
        """Return the number of full calendar days past ``due_at`` (>= 0)."""
        now = now or datetime.utcnow()
        reference = self.returned_at or now
        delta = reference - self.due_at
        return max(delta.days, 0)

    @staticmethod
    def default_due_date(loan_days: int) -> datetime:
        """Return the due date for a loan started right now.

        Centralising this here keeps the "loan duration" rule out of the
        route and service layers.
        """
        return datetime.utcnow() + timedelta(days=loan_days)
