"""Catalogue search helpers.

The public catalogue page uses :func:`search_books` for both the
"browse everything" and "search by keyword" experiences -- an empty
query is treated as "no filter".

We return Flask-SQLAlchemy's :class:`~flask_sqlalchemy.pagination.Pagination`
object directly so the template can render page links without having to
know about the underlying query.
"""

from __future__ import annotations

from typing import Optional

from flask_sqlalchemy.pagination import Pagination
from sqlalchemy import or_  # noqa: F401  -- kept for upcoming author search

from ..extensions import db
from ..models.book import Book


def search_books(
    query: Optional[str],
    page: int = 1,
    per_page: int = 10,
) -> Pagination:
    """Return a paginated list of books matching ``query``.

    Parameters
    ----------
    query:
        Free-text fragment to match against the book title. ``None`` or
        a blank string returns the full catalogue (paginated).
    page:
        1-based page number.
    per_page:
        Number of items per page.

    Returns
    -------
    Pagination
        Flask-SQLAlchemy pagination object; the items live on
        ``.items`` and pagination metadata on ``.page``, ``.pages``,
        ``.has_next``, etc.
    """
    stmt = db.select(Book).order_by(Book.title.asc())

    if query:
        like = f"%{query.strip()}%"
        stmt = stmt.where(Book.title.ilike(like))

    return db.paginate(stmt, page=page, per_page=per_page, error_out=False)
