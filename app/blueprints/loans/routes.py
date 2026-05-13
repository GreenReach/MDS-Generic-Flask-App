"""Patron-facing loan management.

Users can list their own active loans and trigger a return. Admins may
return a loan on behalf of any patron (this is the only place that
admin-only logic leaks into a non-admin blueprint).
"""

from __future__ import annotations

from flask import Blueprint, Response, abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from ...extensions import db
from ...models.loan import Loan
from ...services.loan_service import return_book

loans_bp: Blueprint = Blueprint(
    "loans", __name__, template_folder="../../templates"
)


@loans_bp.route("/my")
@login_required
def my_loans() -> Response | str:
    """List the current user's active loans, soonest due first."""
    active = db.session.execute(
        db.select(Loan)
        .where(Loan.user_id == current_user.id, Loan.returned_at.is_(None))
        .order_by(Loan.due_at.asc())
    ).scalars().all()
    return render_template("loans/my.html", loans=active)


@loans_bp.route("/<int:loan_id>/return", methods=["POST"])
@login_required
def return_loan(loan_id: int) -> Response:
    """Mark ``loan_id`` as returned, optionally creating a fine."""
    loan = db.session.get(Loan, loan_id) or abort(404)
    # A patron may only close their own loans; admins may close any.
    if loan.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    if loan.returned_at is not None:
        flash("This loan has already been returned.", "info")
        return redirect(url_for("loans.my_loans"))

    fine = return_book(loan)
    if fine is not None:
        flash(f"Returned. Overdue fine: ${fine.amount:.2f}.", "warning")
    else:
        flash("Returned on time. Thank you!", "success")
    return redirect(url_for("loans.my_loans"))
