"""Development entry point.

Run the app with either::

    flask --app run.py run

or directly::

    python run.py

The environment is picked from the ``FLASK_CONFIG`` env var and
defaults to ``"development"`` (see :mod:`config`).
"""

from __future__ import annotations

import os

from flask import Flask

from app import create_app

app: Flask = create_app(os.environ.get("FLASK_CONFIG", "development"))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
