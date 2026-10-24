"""Vercel entrypoint — exports WSGI callable `app`."""
import os
import sys
import traceback

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

# Guard against package/name collision returning the module instead of Flask
if not hasattr(_flask_app, "config"):
    raise RuntimeError(
        f"create_app() returned {type(_flask_app)!r}, expected Flask app. "
        "Package name collision with `app`."
    )

_flask_app.config["PROPAGATE_EXCEPTIONS"] = True


def app(environ, start_response):
    try:
        return _flask_app(environ, start_response)
    except Exception:
        tb = traceback.format_exc()
        sys.stderr.write(tb + "\n")
        sys.stderr.flush()
        body = (
            b"<!DOCTYPE html><html><head><meta charset=utf-8><title>500</title></head>"
            b"<body style='font-family:monospace;background:#0a0a0a;color:#eee;padding:24px'>"
            b"<h1 style='color:#f66'>500</h1><pre style='white-space:pre-wrap;font-size:12px'>"
            + tb.encode("utf-8", errors="replace")
            + b"</pre></body></html>"
        )
        start_response(
            "500 Internal Server Error",
            [("Content-Type", "text/html; charset=utf-8"), ("Content-Length", str(len(body)))],
        )
        return [body]


application = _flask_app
