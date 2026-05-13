"""Tests for the authentication blueprint."""


def test_register_then_login(client):
    resp = client.post(
        "/auth/register",
        data={
            "username": "newbie",
            "email": "newbie@example.com",
            "password": "supersecret",
            "confirm": "supersecret",
        },
        follow_redirects=True,
    )
    assert resp.status_code == 200

    resp = client.post(
        "/auth/login",
        data={"username": "newbie", "password": "supersecret"},
        follow_redirects=True,
    )
    assert b"Welcome back" in resp.data


def test_login_with_wrong_password(client, make_user):
    make_user("bob", password="goodpass")
    resp = client.post(
        "/auth/login",
        data={"username": "bob", "password": "wrong"},
        follow_redirects=True,
    )
    assert b"Invalid username or password" in resp.data


def test_logout_requires_login(client):
    resp = client.get("/auth/logout", follow_redirects=False)
    # Anonymous users get redirected to the login page.
    assert resp.status_code in (301, 302)
    assert "/auth/login" in resp.headers["Location"]


def test_admin_page_forbidden_for_normal_user(auth_client):
    resp = auth_client.get("/admin/", follow_redirects=False)
    assert resp.status_code == 403
