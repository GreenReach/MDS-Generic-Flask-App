"""Reservation ORM model.

A :class:`Reservation` lets a patron queue up for a book that is
currently checked out. The application does not (yet) automatically
fulfil reservations when a copy is returned -- that business logic is
left to the staff UI, which sets ``fulfilled_at`` once it has matched a
reservation to a returning copy.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from ..extensions import db


class Reservation(db.Model):
    """A patron's request for a book that is not currently available."""

    __tablename__ = "reservations"
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
    created_at: datetime = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow
    )
    #: ``None`` while the reservation is still in the queue.
    fulfilled_at: Optional[datetime] = db.Column(db.DateTime, nullable=True)

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------
    user = db.relationship("User", back_populates="reservations")
    book = db.relationship("Book", back_populates="reservations")

    # ------------------------------------------------------------------
    # Domain helpers
    # ------------------------------------------------------------------
    @property
    def is_pending(self) -> bool:
        """Return ``True`` if the reservation has not been fulfilled yet."""
        return self.fulfilled_at is None
