"""Book catalogue ORM model.

A :class:`Book` represents a *title* in the catalogue, not an individual
physical copy. Inventory is tracked with two integers: ``total_copies``
(how many we own) and ``available_copies`` (how many are on the shelf
right now). Borrowing decrements ``available_copies``; returning
increments it back.

The ``status`` column is a soft toggle the catalogue layer uses to hide
books from end users without deleting any rows. The default is
``"available"``.
"""

from __future__ import annotations

from typing import Optional

from ..extensions import db


#: Book is on the shelf and may be borrowed.
STATUS_AVAILABLE: str = "available"
#: Book is marked as lost; admins can still see it but patrons cannot.
STATUS_LOST: str = "lost"


class Book(db.Model):
    """A title in the library catalogue."""

    __tablename__ = "books"
    __allow_unmapped__ = True

    # ------------------------------------------------------------------
    # Columns
    # ------------------------------------------------------------------
    id: int = db.Column(db.Integer, primary_key=True)
    title: str = db.Column(db.String(200), nullable=False, index=True)
    author: str = db.Column(db.String(120), nullable=False, index=True)
    #: ISBN-13 is preferred but not required (older books may lack one).
    isbn: Optional[str] = db.Column(db.String(20), unique=True, nullable=True)
    #: Year of (first) publication. Optional because catalogue staff may
    #: not always know it for older donations.
    year: Optional[int] = db.Column(db.Integer, nullable=True)
    total_copies: int = db.Column(db.Integer, nullable=False, default=1)
    available_copies: int = db.Column(db.Integer, nullable=False, default=1)
    status: str = db.Column(
        db.String(16), nullable=False, default=STATUS_AVAILABLE
    )

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------
    loans = db.relationship("Loan", back_populates="book", lazy="dynamic")
    reservations = db.relationship(
        "Reservation", back_populates="book", lazy="dynamic"
    )

    # ------------------------------------------------------------------
    # Domain helpers
    # ------------------------------------------------------------------
    @property
    def is_available(self) -> bool:
        """Return ``True`` iff a patron can borrow this book right now."""
        return self.status == STATUS_AVAILABLE and self.available_copies > 0

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<Book {self.title!r} by {self.author!r}>"
