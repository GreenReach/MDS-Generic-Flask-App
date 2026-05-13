"""Custom view decorators used by the blueprints.

Kept separate from individual blueprints so they can be reused across
features and so the policy ("who is allowed to see what") lives in a
single, easy-to-audit place.
"""

from __future__ import annotations

from functools import wraps
from typing import Any, Callable, TypeVar

from flask import abort
from flask_login import current_user

#: Generic view-function type. We treat decorated views as ``Any``-returning
#: callables -- Flask itself is permissive about return shapes (str, tuple,
#: Response, ...).
F = TypeVar("F", bound=Callable[..., Any])


def role_required(role: str) -> Callable[[F], F]:
    """Reject the request with HTTP 403 unless the user has ``role``.

    Designed to compose with Flask-Login's ``@login_required``: apply
    ``@login_required`` *outermost* so anonymous users are redirected
    to the login page, and ``@role_required(...)`` *inner* so it only
    runs for already-authenticated users.

    Example
    -------
    .. code-block:: python

        @bp.route("/admin")
        @login_required          # outer -- redirects anon users
        @role_required("admin")  # inner -- 403s authed-but-wrong-role
        def dashboard(): ...
    """

    def decorator(view: F) -> F:
        @wraps(view)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if not current_user.is_authenticated or current_user.role != role:
                abort(403)
            return view(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator
