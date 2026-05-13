"""Public landing pages (homepage and "about").

Nothing in this blueprint requires authentication. The homepage shows
a short list of recently-added books to give visitors a feel for the
catalogue.
"""

from __future__ import annotations

from flask import Blueprint, Response, render_template

from ...extensions import db
from ...models.book import Book

main_bp: Blueprint = Blueprint(
    "main", __name__, template_folder="../../templates"
)

#: Number of recently-added books shown on the home page.
_HOMEPAGE_RECENT_LIMIT: int = 6


@main_bp.route("/")
def index() -> Response | str:
    """Render the homepage with the most recently inserted books."""
    recent = db.session.execute(
        db.select(Book).order_by(Book.id.desc()).limit(_HOMEPAGE_RECENT_LIMIT)
    ).scalars().all()
    return render_template("main/index.html", recent_books=recent)


@main_bp.route("/about")
def about() -> Response | str:
    """Render the static "about" page."""
    return render_template("main/about.html")
