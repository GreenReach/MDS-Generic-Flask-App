"""Book catalog: list, search, detail, borrow, reserve."""

from datetime import datetime

from flask import (
    Blueprint,
    abort,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required

from ...extensions import db
from ...models.book import Book
from ...models.reservation import Reservation
from ...services.loan_service import BorrowError, borrow_book
from ...services.search_service import search_books

catalog_bp = Blueprint("catalog", __name__, template_folder="../../templates")


@catalog_bp.route("/")
def list_books():
    page = request.args.get("page", 1, type=int)
    query = request.args.get("q", "", type=str)
    per_page = current_app.config["BOOKS_PER_PAGE"]
    pagination = search_books(query, page=page, per_page=per_page)
    return render_template(
        "catalog/list.html",
        pagination=pagination,
        books=pagination.items,
        query=query,
    )


@catalog_bp.route("/<int:book_id>")
def detail(book_id: int):
    book = db.session.get(Book, book_id) or abort(404)
    return render_template("catalog/detail.html", book=book)


@catalog_bp.route("/<int:book_id>/borrow", methods=["POST"])
@login_required
def borrow(book_id: int):
    book = db.session.get(Book, book_id) or abort(404)
    try:
        borrow_book(current_user, book)
    except BorrowError as exc:
        flash(str(exc), "danger")
        return redirect(url_for("catalog.detail", book_id=book.id))
    flash(f"You borrowed '{book.title}'. Enjoy!", "success")
    return redirect(url_for("loans.my_loans"))


@catalog_bp.route("/<int:book_id>/reserve", methods=["POST"])
@login_required
def reserve(book_id: int):
    book = db.session.get(Book, book_id) or abort(404)
    existing = db.session.execute(
        db.select(Reservation).where(
            Reservation.user_id == current_user.id,
            Reservation.book_id == book.id,
            Reservation.fulfilled_at.is_(None),
        )
    ).scalar_one_or_none()
    if existing is not None:
        flash("You already have a pending reservation for this book.", "info")
    else:
        db.session.add(
            Reservation(user_id=current_user.id, book_id=book.id, created_at=datetime.utcnow())
        )
        db.session.commit()
        flash("Reservation placed.", "success")
    return redirect(url_for("catalog.detail", book_id=book.id))
