# Lab 5 — Navigating a Large Code Project

Welcome! In this lab you will explore **Bibliotheca**, a small but realistic
Flask web application that powers a library: users browse a catalog, borrow
and return books, accumulate fines for late returns, and administrators
manage the book inventory.

The goal of this lab is **not** to build the application from scratch — it
already works. The goal is to learn how a professional developer **reads,
navigates and modifies an unfamiliar codebase**:

1. Form a mental map of the project structure.
2. Trace a feature end-to-end (UI → route → service → model → DB).
3. Diagnose and fix bugs that are hiding in real code.
4. Add small features without breaking existing behavior.

You will use **VS Code** as your IDE. A separate
[VSCODE_CHEATSHEET.md](VSCODE_CHEATSHEET.md) lists the shortcuts you should
practice. Try to use the keyboard rather than the mouse whenever you can.

---

## 0. Setup

```powershell
# from the project root
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# seed the development database (just once)
flask --app run.py seed

# run the dev server
flask --app run.py run
```

Open <http://127.0.0.1:5000>. Log in with one of the seeded accounts:

| User    | Password    | Role  | Notable state                  |
| ------- | ----------- | ----- | ------------------------------ |
| `admin` | `adminpass` | admin | Manages catalog & fines        |
| `alice` | `alicepass` | user  | Has a current loan (Dune)      |
| `bob`   | `bobpass`   | user  | Has an **overdue** loan        |
| `carol` | `carolpass` | user  | Has a pending reservation      |

Run the test suite at least once before changing anything:

```powershell
pytest
```

You should see **2 failing tests**. Those are the bugs you will fix in
Part B. Everything else should pass.

---

## Part A — Comprehension questions

Answer each question in your own words. Where the question asks for a
**file path**, give it relative to the project root, e.g.
`app/services/loan_service.py`.

> **Tip:** practice the VS Code shortcuts as you search — `Ctrl+P` to jump
> to a file by name, `Ctrl+T` to jump to a symbol, `Ctrl+Shift+F` to search
> across the whole project, `F12` to go to definition, and
> `Shift+F12` to find all references.

### Q1 — Application entry point and configuration
- What file does `flask --app run.py run` actually import to build the
  Flask application? Which **factory function** is called?
- Which configuration class is used by default in development, and which
  one is used when the tests run? Give the file path and class names.
- What are the values of `LOAN_DAYS` and `FINE_PER_DAY` in development,
  and how can an operator override them without editing source code?

### Q2 — Tracing a feature: borrowing a book
Trace what happens when **alice** clicks the "Borrow" button on a book
detail page, from the browser all the way down to the database. Your
answer should mention, in order:

1. The HTML template that renders the button.
2. The URL it POSTs to (HTTP method and full path).
3. The blueprint and view function that handle the request.
4. The service function that contains the business logic.
5. The two ORM objects that get mutated and which one gets created.
6. Which database column is decremented, and by how much.

### Q3 — Authorization
The admin pages (`/admin/...`) must reject normal users with **HTTP 403**.

- Which decorator enforces this? Give its file path and a one-line
  description of what it does.
- Find **every** route that uses this decorator. (Use *Find All
  References* — `Shift+F12` — on the decorator name.)
- What is the difference between using `@login_required` alone and
  combining it with `@role_required("admin")`? Why does the order of the
  two decorators matter?

### Q4 — Data model relationships
Open the five files under `app/models/` and answer:

- A `Loan` connects which two other models? What columns implement the
  connection?
- The `Fine` model has a *one-to-one* relationship with `Loan`. Which
  SQLAlchemy argument on the `relationship(...)` call makes it one-to-one
  rather than one-to-many?
- The `User` model defines `loans` and `reservations` relationships, but
  it also inherits behavior (like `is_authenticated`) from a parent class.
  What class, and what does it give us for free?
- Draw (on paper, or as ASCII) the entity-relationship diagram for the
  five models.

### Q5 — Where does the money come from?
A fine is created somewhere in the system whenever a book is returned
late.

- Which **service function** creates a `Fine` row? Give its file path
  and signature.
- Which **helper** turns "days overdue" into an amount in dollars? Where
  is the per-day rate defined?
- Which test verifies that returning a book on time does **not** create
  a fine? Run only that test from the command line. Write down the exact
  `pytest` invocation you used.

---

## Part B — Bug fixes

Two failing tests are pointing at two real bugs. Your job is to make
`pytest` go fully green **without changing the tests**.

For each bug, your write-up should contain:

1. The **failing test name**.
2. The **file and line** of the buggy code.
3. A one-paragraph explanation of *why* it is wrong.
4. The diff (or the new code) of your fix.
5. Confirmation that the test now passes (paste the relevant
   `pytest -k <name>` output).

### Bug 1 — The library is undercharging late readers
- Failing test: `tests/test_loans.py::test_overdue_fine_is_correct`
- Symptom: A book returned 5 days late produces a fine equal to **4**
  days, not 5.
- Hint: the bug is in the math, not in the data. Start by reading the
  service that handles returns.

### Bug 2 — Searching by author returns nothing
- Failing test: `tests/test_catalog.py::test_search_matches_author`
- Symptom: a search for `rowling` does not match the seeded book
  *Harry Potter and the Philosopher's Stone* by **J. K. Rowling**.
- Hint: the search service builds its `WHERE` clause from the user's
  query. Read it carefully — which columns does it actually check?

---

## Part C — Small features

For each feature, follow the same workflow that professional developers
use:

1. **Read** the existing code that you will touch.
2. **Write or extend a test** that fails today but should pass once your
   feature is in place. *(Do this before writing the implementation.)*
3. **Implement** the feature.
4. **Run the whole suite** with `pytest` — every test must still pass.

### Feature 1 — Per-user borrowing limit
Currently a single user can borrow an unlimited number of books at the
same time. Add a configurable maximum.

- Add a new config value `MAX_ACTIVE_LOANS_PER_USER = 3` in
  `config.py`.
- In `app/services/loan_service.py`, when `borrow_book(user, book)` is
  called, count how many of the user's loans are still active
  (`returned_at is None`). If the count is already at or above the
  configured maximum, raise `BorrowError` with a clear message.
- The route that calls `borrow_book` already handles `BorrowError` by
  flashing the message — verify this in
  `app/blueprints/catalog/routes.py` and adjust the flash category if
  needed.
- Add a test in `tests/test_loans.py` (e.g. `test_borrow_blocks_over_limit`)
  that seeds 3 active loans for a user and asserts the 4th raises
  `BorrowError`.

### Feature 2 — "Lost" books are hidden from the catalog
The `Book` model already has a `status` column with a default of
`"available"`. We want admins to be able to mark a book as `"lost"`,
which should:

- Hide the book from the public catalog list and from search results.
- Block the book detail page from offering the **Borrow** button.
- Still be visible inside the admin book list (so an admin can recover
  it).

Implementation outline:

1. Extend `app/services/search_service.py` so the public listing only
   returns books whose `status == "available"`.
2. Update `app/templates/catalog/detail.html` to suppress the borrow
   form when the book is not available (the `Book.is_available`
   property already returns `False` for lost books — use it).
3. Extend `app/blueprints/admin/forms.py` and the admin edit form
   template so an admin can change the status from a dropdown
   (`available` / `lost`).
4. Add a test in `tests/test_catalog.py` (e.g.
   `test_lost_books_are_hidden`) that creates one available and one lost
   book and asserts only the available one appears in `/books/`.

---

## Deliverables

Hand in a single ZIP (or a Git branch / patch) containing:

- The modified source tree (your bug fixes and features).
- A short `report.md` with your answers to Q1–Q5 and the bug write-ups.
- The output of `pytest -q` at the end — it must be **all green** and
  must include your new tests.

Good luck — and remember: when in doubt, **read the test**. Tests are
executable documentation.
