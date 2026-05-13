"""Catalog browsing and search."""

from app.extensions import db
from app.models.book import Book


def _add_book(title, author="Anon", isbn=None, copies=1):
    book = Book(
        title=title,
        author=author,
        isbn=isbn,
        total_copies=copies,
        available_copies=copies,
    )
    db.session.add(book)
    db.session.commit()
    return book


def test_catalog_lists_books(client, app):
    with app.app_context():
        _add_book("The Hobbit", "Tolkien")
        _add_book("Dune", "Herbert")
    resp = client.get("/books/")
    assert resp.status_code == 200
    assert b"The Hobbit" in resp.data
    assert b"Dune" in resp.data


def test_book_detail(client, app):
    with app.app_context():
        book = _add_book("Foundation", "Asimov")
        book_id = book.id
    resp = client.get(f"/books/{book_id}")
    assert resp.status_code == 200
    assert b"Foundation" in resp.data


def test_search_matches_author(client, app):
    """Searching by author should return matching books (case-insensitive)."""
    with app.app_context():
        _add_book("Harry Potter and the Philosopher's Stone", "J. K. Rowling")
        _add_book("Dune", "Frank Herbert")
    resp = client.get("/books/?q=rowling")
    assert resp.status_code == 200
    assert b"Harry Potter" in resp.data, (
        "Search should match by author (case-insensitively): 'rowling' is "
        "expected to find 'Harry Potter ...' by J. K. Rowling."
    )
