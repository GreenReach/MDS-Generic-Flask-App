"""Loan workflow tests."""

from datetime import datetime, timedelta

from app.extensions import db
from app.models.book import Book
from app.models.loan import Loan
from app.models.user import User
from app.services.loan_service import borrow_book, return_book


def _add_book(title="Sample", copies=1):
    book = Book(title=title, author="Anon", total_copies=copies, available_copies=copies)
    db.session.add(book)
    db.session.commit()
    return book


def test_borrow_decrements_available_copies(app, make_user):
    with app.app_context():
        user = make_user("borrower")
        book = _add_book(copies=2)
        loan = borrow_book(user, book)
        assert loan.id is not None
        assert book.available_copies == 1


def test_return_on_time_creates_no_fine(app, make_user):
    with app.app_context():
        user = make_user("borrower")
        book = _add_book()
        loan = borrow_book(user, book)
        fine = return_book(loan)
        assert fine is None
        assert book.available_copies == 1


def test_overdue_fine_is_correct(app, make_user):
    """A book returned 5 days late should produce a fine of 5 * FINE_PER_DAY."""
    with app.app_context():
        user = make_user("late_borrower")
        book = _add_book()
        loan = Loan(
            user_id=user.id,
            book_id=book.id,
            borrowed_at=datetime.utcnow() - timedelta(days=20),
            due_at=datetime.utcnow() - timedelta(days=5),
        )
        book.available_copies -= 1
        db.session.add(loan)
        db.session.commit()

        fine = return_book(loan)
        assert fine is not None
        expected = round(5 * app.config["FINE_PER_DAY"], 2)
        assert fine.amount == expected, (
            f"expected fine for 5 overdue days to be {expected}, got {fine.amount}"
        )
