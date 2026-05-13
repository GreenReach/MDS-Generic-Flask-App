# Lab 5 — Instructor Solutions

> **For laboratory assistants only.** Do not share this file with
> students. It contains the answer key for [LAB.md](LAB.md), the exact
> file/line locations of the planted bugs, reference implementations of
> the two features, and grading rubrics.

---

## Quick map of the codebase

```
run.py                          → flask --app run.py run entry point
wsgi.py                         → production WSGI entry point
config.py                       → Development/Testing/Production configs
app/__init__.py                 → create_app() factory + register_blueprints + seed CLI
app/extensions.py               → db, login_manager, bcrypt singletons
app/utils/decorators.py         → @role_required
app/blueprints/
    main/routes.py              → "/", "/about"
    auth/routes.py              → /auth/login, /auth/logout, /auth/register
    catalog/routes.py           → /books/, /books/<id>, /books/<id>/borrow, /books/<id>/reserve
    loans/routes.py             → /loans/my, /loans/<id>/return
    admin/routes.py             → /admin/, /admin/books/new, /admin/books/<id>/edit, /admin/fines
app/models/                     → User, Book, Loan, Fine, Reservation
app/services/                   → loan_service, fine_service, search_service
seeds/seed_data.py              → idempotent sample data
tests/                          → 13 pytest tests, 2 of them intentionally failing
```

---

## Part A — Answer key

### Q1 — Entry point & configuration
- `flask --app run.py run` imports [run.py](run.py), which calls
  `create_app()` from [app/__init__.py](app/__init__.py).
- Default development config: `DevelopmentConfig` in [config.py](config.py)
  (selected by `create_app()` when `FLASK_CONFIG` is unset).
  Tests use `TestingConfig` (selected in [tests/conftest.py](tests/conftest.py)
  via `create_app("testing")` — in-memory SQLite, CSRF disabled).
- Development values: `LOAN_DAYS = 14`, `FINE_PER_DAY = 0.50`. Both can be
  overridden via the **environment variables** `LOAN_DAYS` and
  `FINE_PER_DAY` (read in `BaseConfig`).

### Q2 — Borrow flow
1. Template: [app/templates/catalog/detail.html](app/templates/catalog/detail.html)
   — the `<form action="...borrow" method="post">` block.
2. URL: **POST** `/books/<book_id>/borrow`.
3. View: `borrow` in [app/blueprints/catalog/routes.py](app/blueprints/catalog/routes.py).
4. Service: `borrow_book(user, book)` in
   [app/services/loan_service.py](app/services/loan_service.py).
5. A new `Loan` row is **created**; the `Book` row is **mutated**
   (the `User` row is read but not modified).
6. `books.available_copies` is **decremented by 1**.

### Q3 — Authorization
- Decorator: `role_required` in
  [app/utils/decorators.py](app/utils/decorators.py). It aborts with
  HTTP 403 if the current user is unauthenticated or does not have the
  required role.
- Used in [app/blueprints/admin/routes.py](app/blueprints/admin/routes.py)
  on every admin view: `dashboard`, `new_book`, `edit_book`, `fines`.
- `@login_required` alone redirects anonymous users to `/auth/login`.
  Adding `@role_required("admin")` additionally checks the role and
  returns 403 for authenticated-but-wrong-role users.
  Order matters because decorators wrap **bottom-up**:
  ```python
  @login_required        # outer — runs first, redirects anon
  @role_required("admin")# inner — only sees authenticated users
  def view(): ...
  ```
  If reversed, an anonymous user would hit `role_required` first and
  receive a 403 instead of a friendlier redirect to the login page.

### Q4 — Models
- `Loan` connects `User` and `Book` via the FK columns `user_id`
  (→ `users.id`) and `book_id` (→ `books.id`).
- One-to-one is enforced by `uselist=False` on the
  `Loan.fine = db.relationship("Fine", ..., uselist=False)` line, plus
  `unique=True` on `Fine.loan_id`.
- `User` inherits from `flask_login.UserMixin`, which provides
  `is_authenticated`, `is_active`, `is_anonymous`, and `get_id()`.
- ER diagram:
  ```
       User 1───* Loan *───1 Book
        │                    │
        └───*  Reservation  *┘
                   │
                   ▼
                  (no further relations)

       Loan 1───1 Fine
  ```

### Q5 — Fines
- `return_book(loan)` in
  [app/services/loan_service.py](app/services/loan_service.py)
  is the function that creates a `Fine`.
- `calculate_fine(days_overdue)` in
  [app/services/fine_service.py](app/services/fine_service.py).
  Per-day rate is `FINE_PER_DAY` from `BaseConfig` in
  [config.py](config.py).
- Test: `tests/test_loans.py::test_return_on_time_creates_no_fine`.
  Invocation: `pytest tests/test_loans.py::test_return_on_time_creates_no_fine`.

---

## Part B — Bug locations and fixes

### Bug 1 — Off-by-one in days_overdue
**File:** [app/services/loan_service.py](app/services/loan_service.py)
**Function:** `return_book`
**Buggy line:**
```python
raw_days = (loan.returned_at - loan.due_at).days
days_overdue = max(0, raw_days - 1)   # ← extra "- 1"
```
**Fix:**
```python
days_overdue = max(0, raw_days)
```
**Verify:**
```
pytest tests/test_loans.py::test_overdue_fine_is_correct -q
```

### Bug 2 — Search ignores the author column
**File:** [app/services/search_service.py](app/services/search_service.py)
**Function:** `search_books`
**Buggy line:**
```python
stmt = stmt.where(Book.title.ilike(like))   # only filters on title
```
**Fix:**
```python
from sqlalchemy import or_  # already imported
stmt = stmt.where(or_(Book.title.ilike(like), Book.author.ilike(like)))
```
Using `.ilike(...)` (rather than `.like(...)`) keeps the match
case-insensitive on databases whose `LIKE` is case-sensitive (e.g.
PostgreSQL). On SQLite both work for ASCII text, but `ilike` is the
portable choice. Reject solutions that only add `Book.author` but drop
the title check.
**Verify:**
```
pytest tests/test_catalog.py::test_search_matches_author -q
```

---

## Part C — Reference implementations

### Feature 1 — Borrowing limit

**[config.py](config.py)** — add to `BaseConfig`:
```python
MAX_ACTIVE_LOANS_PER_USER = int(os.environ.get("MAX_ACTIVE_LOANS_PER_USER", 3))
```

**[app/services/loan_service.py](app/services/loan_service.py)** — at
the top of `borrow_book`:
```python
def borrow_book(user: User, book: Book) -> Loan:
    if not book.is_available:
        raise BorrowError("This book is not available for borrowing.")

    limit = current_app.config["MAX_ACTIVE_LOANS_PER_USER"]
    active = Loan.query.filter_by(user_id=user.id, returned_at=None).count()
    if active >= limit:
        raise BorrowError(
            f"You already have the maximum of {limit} active loans."
        )
    ...
```

**Test** (add to `tests/test_loans.py`):
```python
def test_borrow_blocks_over_limit(app, make_user):
    with app.app_context():
        user = make_user("greedy")
        for i in range(3):
            book = _add_book(title=f"Book {i}")
            borrow_book(user, book)
        extra = _add_book(title="One Too Many")
        import pytest
        from app.services.loan_service import BorrowError
        with pytest.raises(BorrowError):
            borrow_book(user, extra)
```

### Feature 2 — Hide "lost" books from the catalog

**[app/services/search_service.py](app/services/search_service.py)**:
```python
stmt = (
    db.select(Book)
    .where(Book.status == "available")
    .order_by(Book.title.asc())
)
```

**[app/blueprints/admin/forms.py](app/blueprints/admin/forms.py)** — add
to `BookForm`:
```python
from wtforms import SelectField
status = SelectField(
    "Status",
    choices=[("available", "Available"), ("lost", "Lost")],
    default="available",
)
```

**[app/templates/admin/book_form.html](app/templates/admin/book_form.html)** —
render the `status` field next to the other inputs.

**[app/blueprints/admin/routes.py](app/blueprints/admin/routes.py)** — in
`edit_book` (and `new_book` if desired) copy `form.status.data` onto the
`Book.status` column before committing.

**[app/templates/catalog/detail.html](app/templates/catalog/detail.html)** —
already uses `book.is_available`, which returns `False` for lost books
(thanks to the existing `is_available` property). No change needed if
the template is already gated on `book.is_available`; otherwise wrap the
borrow form in `{% if book.is_available %}...{% endif %}`.

**Test** (add to `tests/test_catalog.py`):
```python
def test_lost_books_are_hidden(client, app):
    with app.app_context():
        _add_book("Available Title", "Author A")
        lost = _add_book("Lost Title", "Author B")
        lost.status = "lost"
        db.session.commit()
    resp = client.get("/books/")
    assert b"Available Title" in resp.data
    assert b"Lost Title" not in resp.data
```

---

## Grading rubric (suggested, total 100 pts)

| Section                                     | Points |
| ------------------------------------------- | ------ |
| Q1 — Entry point & config                   |   6    |
| Q2 — Borrow trace (full path, all 6 steps)  |  10    |
| Q3 — Authorization (decorator + references) |   8    |
| Q4 — Models (FKs, uselist, UserMixin, ERD)  |  10    |
| Q5 — Fines (function names + test command)  |   6    |
| Bug 1 fix + passing test                    |  10    |
| Bug 2 fix + passing test (both fields)      |  10    |
| Feature 1 (impl + new test passes)          |  20    |
| Feature 2 (impl + new test passes)          |  20    |

Deduct points for: not running the full test suite at the end, modifying
the originally-failing tests instead of the source, or leaving the test
suite red after their changes.

---

## Common student traps to watch for

1. **Fixing Bug 1 inside the test** — some students will edit the test
   instead of the source. Reject.
2. **Fixing Bug 2 by lowercasing the input only** — the column side
   must be handled too if they choose the `func.lower` route. `ilike`
   is the cleanest.
3. **Bug 2 fix that drops the title check** — they must keep title AND
   add author. Verify with both `?q=harry` and `?q=rowling`.
4. **Feature 1 implemented in the route, not the service** — discourage;
   business logic belongs in the service so it stays testable.
5. **Feature 2 forgetting to filter search results** — only filtering
   the catalog list lets students "find" lost books via the search box.
6. **Test database leaks** — students who add an `_add_book(...)` helper
   without rolling back can cause cross-test pollution. Each test owns
   its own `app` fixture (see [tests/conftest.py](tests/conftest.py)),
   so this is usually fine, but watch for shared module-level state.

---

## Useful commands cheat-sheet for instructors

```powershell
# Reset & reseed the dev database
Remove-Item .\instance\library.db -ErrorAction SilentlyContinue
flask --app run.py seed

# Run a single test
pytest tests/test_loans.py::test_overdue_fine_is_correct -v

# Run only tests matching a keyword
pytest -k "search or overdue" -v

# Show coverage (after `pip install coverage`)
coverage run -m pytest ; coverage report -m
```
