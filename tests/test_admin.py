"""Admin blueprint tests."""

from app.extensions import db
from app.models.book import Book


def test_dashboard_requires_admin_role(auth_client):
    resp = auth_client.get("/admin/")
    assert resp.status_code == 403


def test_admin_can_create_book(admin_client, app):
    resp = admin_client.post(
        "/admin/books/new",
        data={
            "title": "New Title",
            "author": "Someone",
            "isbn": "1234567890",
            "year": "2020",
            "total_copies": "2",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    with app.app_context():
        book = db.session.execute(
            db.select(Book).where(Book.title == "New Title")
        ).scalar_one()
        assert book.available_copies == 2


def test_admin_can_edit_book(admin_client, app):
    with app.app_context():
        book = Book(title="Old", author="X", total_copies=1, available_copies=1)
        db.session.add(book)
        db.session.commit()
        book_id = book.id

    resp = admin_client.post(
        f"/admin/books/{book_id}/edit",
        data={
            "title": "Renamed",
            "author": "X",
            "isbn": "",
            "year": "",
            "total_copies": "3",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200
    with app.app_context():
        book = db.session.get(Book, book_id)
        assert book.title == "Renamed"
        assert book.total_copies == 3
