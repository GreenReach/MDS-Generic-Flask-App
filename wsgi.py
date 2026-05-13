"""WSGI entry point for production application servers.

Gunicorn (Linux) or Waitress (Windows) point at the
:data:`application` callable exported here::

    gunicorn wsgi:application
    waitress-serve --listen=0.0.0.0:8000 wsgi:application

The production config is loaded explicitly to avoid accidentally
shipping debug mode.
"""

from __future__ import annotations

from flask import Flask

from app import create_app

application: Flask = create_app("production")
