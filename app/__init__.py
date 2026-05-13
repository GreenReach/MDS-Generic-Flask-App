"""Application factory for the Bibliotheca library application.

This module exposes a single public entry point, :func:`create_app`,
which wires together:

* the configuration object selected by ``config_name``,
* every Flask extension we use (SQLAlchemy, Flask-Login, Bcrypt),
* the five blueprints that make up the public surface of the app,
* error handlers for the HTTP statuses we surface to end users,
* the ``flask seed`` CLI command,
* the template-globals context processor.

Keeping all of this in a factory (rather than at module import time)
lets the test suite spin up isolated app instances against an
in-memory database without polluting the production configuration.
"""

from __future__ import annotations

from typing import Optional

from flask import Flask, render_template
from werkzeug.exceptions import HTTPException

from config import config_by_name

from .extensions import bcrypt, db, login_manager


def create_app(config_name: str = "development") -> Flask:
    """Build and return a fully-wired :class:`flask.Flask` instance.

    Parameters
    ----------
    config_name:
        Key into :data:`config.config_by_name`. Defaults to
        ``"development"``.
    """
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_object(config_by_name[config_name])

    _register_extensions(app)
    _register_blueprints(app)
    _register_error_handlers(app)
    _register_cli(app)
    _register_context_processors(app)

    with app.app_context():
        # For the lab we deliberately skip Alembic. Tables are created
        # on first run if the SQLite file does not exist yet -- a real
        # production deployment would replace this with a managed
        # migration step.
        from . import models  # noqa: F401  -- import for side effects

        db.create_all()

    return app


# ----------------------------------------------------------------------
# Wiring helpers (kept private to the factory)
# ----------------------------------------------------------------------
def _register_extensions(app: Flask) -> None:
    """Bind the unbound extension singletons to ``app``."""
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    from .models.user import User

    @login_manager.user_loader
    def load_user(user_id: str) -> Optional[User]:
        """Reload a user from the session cookie."""
        return db.session.get(User, int(user_id))


def _register_blueprints(app: Flask) -> None:
    """Mount the public-facing blueprints under their URL prefixes."""
    from .blueprints.admin.routes import admin_bp
    from .blueprints.auth.routes import auth_bp
    from .blueprints.catalog.routes import catalog_bp
    from .blueprints.loans.routes import loans_bp
    from .blueprints.main.routes import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(catalog_bp, url_prefix="/books")
    app.register_blueprint(loans_bp, url_prefix="/loans")
    app.register_blueprint(admin_bp, url_prefix="/admin")


def _register_error_handlers(app: Flask) -> None:
    """Map the HTTP errors we want to brand to friendlier templates."""

    @app.errorhandler(403)
    def forbidden(_: HTTPException):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(_: HTTPException):
        return render_template("errors/404.html"), 404


def _register_cli(app: Flask) -> None:
    """Attach project-specific ``flask <command>`` entries."""
    from seeds.seed_data import seed_command

    app.cli.add_command(seed_command)


def _register_context_processors(app: Flask) -> None:
    """Inject globals available to every Jinja template."""

    @app.context_processor
    def inject_globals() -> dict:
        return {"app_name": "Bibliotheca"}
