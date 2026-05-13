"""Fine ORM model.

A :class:`Fine` is the financial penalty attached to a late
:class:`~app.models.loan.Loan`. The relationship is one-to-one
(enforced via ``unique=True`` on ``loan_id`` and ``uselist=False`` on
the back-reference) -- a single loan can produce at most one fine.

Marking a fine as ``paid`` is currently done directly in the admin UI;
the application has no payment provider integration.
"""

from __future__ import annotations

from ..extensions import db


class Fine(db.Model):
    """A monetary penalty for a single overdue loan."""

    __tablename__ = "fines"
    __allow_unmapped__ = True

    # ------------------------------------------------------------------
    # Columns
    # ------------------------------------------------------------------
    id: int = db.Column(db.Integer, primary_key=True)
    loan_id: int = db.Column(
        db.Integer,
        db.ForeignKey("loans.id"),
        nullable=False,
        unique=True,  # one fine per loan
    )
    #: Amount in the application's reporting currency (USD by default).
    amount: float = db.Column(db.Float, nullable=False, default=0.0)
    paid: bool = db.Column(db.Boolean, nullable=False, default=False)

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------
    loan = db.relationship("Loan", back_populates="fine")
