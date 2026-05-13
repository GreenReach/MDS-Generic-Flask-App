"""Shared pytest fixtures.

Each test gets a brand-new, in-memory SQLite database and freshly-seeded
users so tests stay isolated.
"""

import pytest

from app import create_app
from app.extensions import db
from app.models.user import User


@pytest.fixture()
def app():
    app = create_app("testing")
    with app.app_context():
        db.drop_all()
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def make_user(app):
    """Factory that creates a user and commits it to the test DB."""

    def _make(username="testuser", email=None, password="secret123", role="user"):
        user = User(username=username, email=email or f"{username}@example.com", role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user

    return _make


def _login(client, username, password):
    return client.post(
        "/auth/login",
        data={"username": username, "password": password},
        follow_redirects=True,
    )


@pytest.fixture()
def auth_client(client, make_user):
    make_user("alice", password="alicepass")
    _login(client, "alice", "alicepass")
    return client


@pytest.fixture()
def admin_client(client, make_user):
    make_user("rootadmin", password="adminpass", role="admin")
    _login(client, "rootadmin", "adminpass")
    return client
