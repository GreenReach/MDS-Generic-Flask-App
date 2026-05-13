"""Authentication views: login, logout, registration.

The routes here intentionally stay thin: form validation lives in
:mod:`app.blueprints.auth.forms`, password hashing lives on the
:class:`~app.models.user.User` model, and Flask-Login owns the session
state. The view's job is only to orchestrate.
"""

from __future__ import annotations

from flask import (
    Blueprint,
    Response,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from flask_login import current_user, login_required, login_user, logout_user

from ...extensions import db
from ...models.user import User
from .forms import LoginForm, RegisterForm

auth_bp: Blueprint = Blueprint(
    "auth", __name__, template_folder="../../templates"
)


@auth_bp.route("/login", methods=["GET", "POST"])
def login() -> Response | str:
    """Authenticate an existing user and start a session."""
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.execute(
            db.select(User).where(User.username == form.username.data)
        ).scalar_one_or_none()
        if user is not None and user.check_password(form.password.data):
            login_user(user)
            flash(f"Welcome back, {user.username}!", "success")
            # ``next`` may have been added by Flask-Login's redirect
            # for protected pages -- preserve it so the user lands
            # back where they tried to go.
            next_url = request.args.get("next") or url_for("main.index")
            return redirect(next_url)
        flash("Invalid username or password.", "danger")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout() -> Response:
    """End the current user's session."""
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.index"))


@auth_bp.route("/register", methods=["GET", "POST"])
def register() -> Response | str:
    """Create a new user account.

    Uniqueness of ``username`` and ``email`` is checked against the
    DB here (rather than in the form) so we can return a clean flash
    message instead of a 500 from the unique constraint.
    """
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = RegisterForm()
    if form.validate_on_submit():
        exists = db.session.execute(
            db.select(User).where(
                (User.username == form.username.data)
                | (User.email == form.email.data)
            )
        ).scalar_one_or_none()
        if exists:
            flash("Username or email already in use.", "danger")
        else:
            user = User(
                username=form.username.data,
                email=form.email.data,
                role="user",
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash("Account created. You can now log in.", "success")
            return redirect(url_for("auth.login"))

    return render_template("auth/register.html", form=form)
