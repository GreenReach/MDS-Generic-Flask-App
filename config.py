"""Application configuration objects.

Three environments are supported out of the box:

* :class:`DevelopmentConfig` -- local development against a SQLite file.
* :class:`TestingConfig`     -- in-memory SQLite, CSRF disabled.
* :class:`ProductionConfig`  -- deliberately minimal; expected to be
  driven by environment variables on the host.

The environment is selected via the ``FLASK_CONFIG`` environment
variable (or by passing the name directly to
:func:`app.create_app`). Sensitive values (``SECRET_KEY``,
``DATABASE_URL``, ...) must always be supplied via environment
variables in production -- the defaults here are for development
convenience only.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Type

#: Project root, used to anchor the development SQLite file.
BASE_DIR: Path = Path(__file__).resolve().parent


class BaseConfig:
    """Settings common to every environment."""

    #: Cryptographic key used for sessions and CSRF tokens. **Must** be
    #: overridden in production via the ``SECRET_KEY`` env var.
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "dev-secret-change-me")

    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

    # ------------------------------------------------------------------
    # Domain configuration consumed by the service layer
    # ------------------------------------------------------------------
    #: Per-day overdue penalty in the reporting currency.
    FINE_PER_DAY: float = float(os.environ.get("FINE_PER_DAY", "0.50"))
    #: Default loan duration (in days) used when a new loan is created.
    LOAN_DAYS: int = int(os.environ.get("LOAN_DAYS", "14"))
    #: Pagination size for the public catalogue listing.
    BOOKS_PER_PAGE: int = 10


class DevelopmentConfig(BaseConfig):
    """Local development: debug mode, SQLite file in the project root."""

    DEBUG: bool = True
    SQLALCHEMY_DATABASE_URI: str = os.environ.get(
        "DATABASE_URL", f"sqlite:///{BASE_DIR / 'library.db'}"
    )


class TestingConfig(BaseConfig):
    """Pytest: in-memory DB, CSRF off, fixed secret for reproducibility."""

    TESTING: bool = True
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///:memory:"
    WTF_CSRF_ENABLED: bool = False
    SECRET_KEY: str = "testing-secret"


class ProductionConfig(BaseConfig):
    """Production defaults; expected to be overridden via env vars."""

    DEBUG: bool = False
    SQLALCHEMY_DATABASE_URI: str = os.environ.get(
        "DATABASE_URL", "sqlite:///library.db"
    )


#: Lookup table consumed by :func:`app.create_app`.
config_by_name: Dict[str, Type[BaseConfig]] = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
