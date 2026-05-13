"""User account ORM model.

The :class:`User` aggregate is the security principal of the application.
It owns its credentials (a bcrypt-hashed password), an authorisation role
(``"user"`` or ``"admin"``) and the two collections that describe what a
user has done with the catalogue: their :class:`~app.models.loan.Loan`
records and their :class:`~app.models.reservation.Reservation` queue.

The model intentionally inherits from :class:`flask_login.UserMixin` so
Flask-Login can rely on the standard interface (``is_authenticated``,
``get_id`` and friends) without us re-implementing it.
"""

from __future__ import annotations

from flask_login import UserMixin

from ..extensions import bcrypt, db


# Roles are kept as plain strings for portability with WTForms <SelectField>
# and to avoid the storage cost of an Enum column on SQLite. If the project
# grows we can promote this to ``sqlalchemy.Enum``.
ROLE_USER: str = "user"
ROLE_ADMIN: str = "admin"


class User(UserMixin, db.Model):
    """A registered library patron or administrator."""

    __tablename__ = "users"
    # Opt into the SQLAlchemy 1.x style of plain class-level annotations
    # alongside ``db.Column``. Avoids needing ``Mapped[...]`` everywhere.
    __allow_unmapped__ = True

    # ------------------------------------------------------------------
    # Columns
    # ------------------------------------------------------------------
    id: int = db.Column(db.Integer, primary_key=True)
    username: str = db.Column(
        db.String(64), unique=True, nullable=False, index=True
    )
    email: str = db.Column(
        db.String(120), unique=True, nullable=False, index=True
    )
    #: bcrypt hash of the user's password. Never stored in cleartext.
    password_hash: str = db.Column(db.String(128), nullable=False)
    role: str = db.Column(db.String(16), nullable=False, default=ROLE_USER)

    # ------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------
    #: All loan records (active or returned) owned by this user.
    loans = db.relationship("Loan", back_populates="user", lazy="dynamic")
    #: All reservations placed by this user (pending or fulfilled).
    reservations = db.relationship(
        "Reservation", back_populates="user", lazy="dynamic"
    )

    # ------------------------------------------------------------------
    # Credentials
    # ------------------------------------------------------------------
    def set_password(self, raw_password: str) -> None:
        """Hash ``raw_password`` with bcrypt and store the digest."""
        self.password_hash = bcrypt.generate_password_hash(
            raw_password
        ).decode("utf-8")

    def check_password(self, raw_password: str) -> bool:
        """Return ``True`` iff ``raw_password`` matches the stored hash."""
        return bcrypt.check_password_hash(self.password_hash, raw_password)

    # ------------------------------------------------------------------
    # Authorisation helpers
    # ------------------------------------------------------------------
    @property
    def is_admin(self) -> bool:
        """Convenience used by templates and the ``role_required`` decorator."""
        return self.role == ROLE_ADMIN

    # ------------------------------------------------------------------
    # Misc
    # ------------------------------------------------------------------
    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<User {self.username} ({self.role})>"
