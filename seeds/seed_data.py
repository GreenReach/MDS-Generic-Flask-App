"""``flask seed`` -- populate the database with realistic sample data.

Running the command twice is safe: every insert is guarded by a
lookup, so the seed is fully idempotent. The seed deliberately
creates a mix of "happy path" data (Alice's loan is on time) and
"sad path" data (Bob's loan is overdue) so the admin dashboard and
fine flow have something to show.

Developer accounts created (do **not** use these passwords in
production):

* ``admin / adminpass``  -- administrator role
* ``alice / alicepass``  -- regular user with a current loan
* ``bob   / bobpass``    -- regular user with an *overdue* loan
* ``carol / carolpass``  -- regular user with a pending reservation
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, Tuple

import click
from flask.cli import with_appcontext

from app.extensions import db
from app.models.book import Book
from app.models.loan import Loan
from app.models.reservation import Reservation
from app.models.user import User


#: Catalogue seed: ``(title, author, isbn, year, total_copies)``.
SAMPLE_BOOKS: List[Tuple[str, str, str, int, int]] = [
    ("The Pragmatic Programmer", "Andrew Hunt", "9780201616224", 1999, 3),
    ("Clean Code", "Robert C. Martin", "9780132350884", 2008, 2),
    ("Refactoring", "Martin Fowler", "9780201485677", 1999, 2),
    ("Design Patterns", "Erich Gamma", "9780201633610", 1994, 1),
    ("Domain-Driven Design", "Eric Evans", "9780321125217", 2003, 1),
    ("Code Complete", "Steve McConnell", "9780735619678", 2004, 2),
    ("Working Effectively with Legacy Code", "Michael Feathers", "9780131177055", 2004, 1),
    ("The Mythical Man-Month", "Frederick P. Brooks", "9780201835953", 1975, 1),
    ("Structure and Interpretation of Computer Programs", "Harold Abelson", "9780262510875", 1996, 1),
    ("Introduction to Algorithms", "Thomas H. Cormen", "9780262033848", 2009, 3),
    ("Harry Potter and the Philosopher's Stone", "J. K. Rowling", "9780747532699", 1997, 4),
    ("Harry Potter and the Chamber of Secrets", "J. K. Rowling", "9780747538493", 1998, 3),
    ("The Hobbit", "J. R. R. Tolkien", "9780547928227", 1937, 2),
    ("The Lord of the Rings", "J. R. R. Tolkien", "9780544003415", 1954, 2),
    ("1984", "George Orwell", "9780451524935", 1949, 3),
    ("Brave New World", "Aldous Huxley", "9780060850524", 1932, 2),
    ("Fahrenheit 451", "Ray Bradbury", "9781451673319", 1953, 2),
    ("To Kill a Mockingbird", "Harper Lee", "9780061120084", 1960, 2),
    ("Pride and Prejudice", "Jane Austen", "9780141439518", 1813, 1),
    ("Crime and Punishment", "Fyodor Dostoevsky", "9780140449136", 1866, 1),
    ("The Brothers Karamazov", "Fyodor Dostoevsky", "9780374528379", 1880, 1),
    ("Moby-Dick", "Herman Melville", "9780142437247", 1851, 1),
    ("Foundation", "Isaac Asimov", "9780553293357", 1951, 2),
    ("Dune", "Frank Herbert", "9780441172719", 1965, 3),
    ("Neuromancer", "William Gibson", "9780441569595", 1984, 1),
]


def _get_or_create_user(
    username: str, email: str, password: str, role: str
) -> User:
    """Return the existing user with ``username`` or create one."""
    user = db.session.execute(
        db.select(User).where(User.username == username)
    ).scalar_one_or_none()
    if user is None:
        user = User(username=username, email=email, role=role)
        user.set_password(password)
        db.session.add(user)
    return user


def _seed() -> None:
    """Insert (or skip) all sample rows in a single committed batch."""
    admin = _get_or_create_user("admin", "admin@example.com", "adminpass", "admin")
    alice = _get_or_create_user("alice", "alice@example.com", "alicepass", "user")
    bob = _get_or_create_user("bob", "bob@example.com", "bobpass", "user")
    carol = _get_or_create_user("carol", "carol@example.com", "carolpass", "user")

    # Books -- skip any that already exist by ISBN.
    for title, author, isbn, year, copies in SAMPLE_BOOKS:
        exists = db.session.execute(
            db.select(Book).where(Book.isbn == isbn)
        ).scalar_one_or_none()
        if exists is None:
            db.session.add(
                Book(
                    title=title,
                    author=author,
                    isbn=isbn,
                    year=year,
                    total_copies=copies,
                    available_copies=copies,
                )
            )

    db.session.commit()

    # A few realistic loans -- including one that is already overdue
    # so the fine flow has data to work with. Only inserted on a
    # fresh DB (i.e. when no loans exist yet).
    has_loans = db.session.execute(db.select(Loan).limit(1)).scalar_one_or_none()
    if has_loans is None:
        dune = db.session.execute(
            db.select(Book).where(Book.title == "Dune")
        ).scalar_one()
        clean_code = db.session.execute(
            db.select(Book).where(Book.title == "Clean Code")
        ).scalar_one()
        nineteen = db.session.execute(
            db.select(Book).where(Book.title == "1984")
        ).scalar_one()

        now = datetime.utcnow()
        loans: List[Loan] = [
            Loan(
                user_id=alice.id,
                book_id=dune.id,
                borrowed_at=now - timedelta(days=3),
                due_at=now + timedelta(days=11),
            ),
            Loan(
                user_id=bob.id,
                book_id=clean_code.id,
                borrowed_at=now - timedelta(days=20),
                due_at=now - timedelta(days=6),  # overdue on purpose
            ),
        ]
        for loan in loans:
            db.session.add(loan)
        # Reflect the loans in the inventory counters.
        dune.available_copies -= 1
        clean_code.available_copies -= 1

        db.session.add(
            Reservation(
                user_id=carol.id, book_id=nineteen.id, created_at=now
            )
        )

    db.session.commit()


@click.command("seed")
@with_appcontext
def seed_command() -> None:
    """Populate the database with sample users, books, loans and reservations."""
    _seed()
    click.echo("Seed data inserted.")
    click.echo("Accounts:")
    click.echo("  admin / adminpass   (admin)")
    click.echo("  alice / alicepass   (user)")
    click.echo("  bob   / bobpass     (user, has overdue loan)")
    click.echo("  carol / carolpass   (user)")
