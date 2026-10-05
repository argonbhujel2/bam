"""Vercel entrypoint — exports a plain WSGI callable named `app`."""
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from dotenv import load_dotenv
load_dotenv(os.path.join(ROOT, ".env"))

from app import create_app

_flask_app = create_app(
    os.environ.get("FLASK_ENV")
    or ("production" if os.environ.get("VERCEL") else "development")
)


def app(environ, start_response):
    """Explicit WSGI entry so Vercel can always detect the interface."""
    return _flask_app(environ, start_response)


# Also expose the Flask instance for tooling that expects it
application = _flask_app
