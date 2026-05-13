"""Shared Flask extension singletons.

Keeping the extension instances in their own module avoids circular
imports between the application factory (which needs to call
``init_app`` on each of them) and the blueprints / models (which need
to import the configured instance to issue queries or hash passwords).

The instances are *unbound* at import time; :func:`app.create_app`
binds them to a concrete :class:`flask.Flask` application during
start-up.
"""

from __future__ import annotations

from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

#: Single SQLAlchemy session/engine registry shared by every model.
db: SQLAlchemy = SQLAlchemy()

#: Flask-Login user-session manager. Configured to redirect anonymous
#: users to the login view and flash a warning-styled message.
login_manager: LoginManager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message_category = "warning"

#: Bcrypt hasher used by :class:`app.models.user.User` for password
#: storage and verification.
bcrypt: Bcrypt = Bcrypt()
