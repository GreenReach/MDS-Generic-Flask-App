"""Admin dashboard: high-level stats, book CRUD, fines overview.

Every view in this blueprint is gated by
``@login_required`` + ``@role_required("admin")`` -- anonymous users
are redirected to the login page, authenticated non-admins receive
a 403.
"""

from __future__ import annotations

from typing import Dict

from flask import Blueprint, Response, abort, flash, redirect, render_template, url_for
from flask_login import login_required

from ...extensions import db
from ...models.book import Book
from ...models.fine import Fine
from ...models.loan import Loan
from ...models.user import User
from ...utils.decorators import role_required
from .forms import BookForm

admin_bp: Blueprint = Blueprint(
    "admin", __name__, template_folder="../../templates"
)


@admin_bp.route("/")
@login_required
@role_required("admin")
def dashboard() -> Response | str:
    """Render the admin landing page with at-a-glance counters."""
    counts: Dict[str, int] = {
        "users": db.session.scalar(
            db.select(db.func.count()).select_from(User)
        ),
        "books": db.session.scalar(
            db.select(db.func.count()).select_from(Book)
        ),
        "active_loans": db.session.scalar(
            db.select(db.func.count())
            .select_from(Loan)
            .where(Loan.returned_at.is_(None))
        ),
        "unpaid_fines": db.session.scalar(
            db.select(db.func.count())
            .select_from(Fine)
            .where(Fine.paid.is_(False))
        ),
    }
    return render_template("admin/dashboard.html", counts=counts)


@admin_bp.route("/books/new", methods=["GET", "POST"])
@login_required
@role_required("admin")
def new_book() -> Response | str:
    """Create a new :class:`~app.models.book.Book` from a form post."""
    form = BookForm()
    if form.validate_on_submit():
        book = Book(
            title=form.title.data,
            author=form.author.data,
            isbn=form.isbn.data or None,
            year=form.year.data,
            total_copies=form.total_copies.data,
            # New books are fully available on creation.
            available_copies=form.total_copies.data,
        )
        db.session.add(book)
        db.session.commit()
        flash(f"Added '{book.title}'.", "success")
        return redirect(url_for("catalog.detail", book_id=book.id))
    return render_template("admin/book_form.html", form=form, mode="new")


@admin_bp.route("/books/<int:book_id>/edit", methods=["GET", "POST"])
@login_required
@role_required("admin")
def edit_book(book_id: int) -> Response | str:
    """Edit an existing book; preserves loan-in-progress accounting."""
    book = db.session.get(Book, book_id) or abort(404)
    form = BookForm(obj=book)
    if form.validate_on_submit():
        # Apply the delta to ``available_copies`` so books that are
        # currently out on loan stay accounted for correctly.
        diff = form.total_copies.data - book.total_copies
        book.title = form.title.data
        book.author = form.author.data
        book.isbn = form.isbn.data or None
        book.year = form.year.data
        book.total_copies = form.total_copies.data
        book.available_copies = max(0, book.available_copies + diff)
        db.session.commit()
        flash("Book updated.", "success")
        return redirect(url_for("catalog.detail", book_id=book.id))
    return render_template(
        "admin/book_form.html", form=form, mode="edit", book=book
    )


@admin_bp.route("/fines")
@login_required
@role_required("admin")
def fines() -> Response | str:
    """List every fine, unpaid first."""
    rows = db.session.execute(
        db.select(Fine).order_by(Fine.paid.asc(), Fine.id.desc())
    ).scalars().all()
    return render_template("admin/fines.html", fines=rows)
