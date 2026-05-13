"""WTForms used by the :mod:`app.blueprints.auth` blueprint.

These forms validate user input *before* it reaches the service or ORM
layer. They do not enforce business rules (uniqueness, role rules,
...): those live in the route / service layer.
"""

from __future__ import annotations

from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length


class LoginForm(FlaskForm):
    """Credential prompt for an existing account."""

    username = StringField(
        "Username", validators=[DataRequired(), Length(max=64)]
    )
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log in")


class RegisterForm(FlaskForm):
    """New-account form.

    Uniqueness of ``username`` and ``email`` is **not** enforced here
    (WTForms cannot run DB queries cleanly without context); the
    ``register`` view double-checks against the database before
    persisting.
    """

    username = StringField(
        "Username", validators=[DataRequired(), Length(min=3, max=64)]
    )
    email = StringField(
        "Email", validators=[DataRequired(), Email(), Length(max=120)]
    )
    password = PasswordField(
        "Password", validators=[DataRequired(), Length(min=6, max=128)]
    )
    confirm = PasswordField(
        "Confirm password",
        validators=[
            DataRequired(),
            EqualTo("password", message="Passwords must match."),
        ],
    )
    submit = SubmitField("Create account")
