"""Vercel entrypoint — WSGI `app` + visible errors for debugging."""
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

# Surface real errors while stabilizing deploy
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
            b"<body style='font-family:ui-monospace,monospace;background:#0a0a0a;color:#e8e8e8;padding:24px'>"
            b"<h1 style='color:#f66'>500 Internal Server Error</h1>"
            b"<p>Copy this traceback and send it for a fix:</p>"
            b"<pre style='white-space:pre-wrap;font-size:12px;background:#111;padding:16px;border:1px solid #333;border-radius:8px'>"
            + tb.encode("utf-8", errors="replace")
            + b"</pre></body></html>"
        )
        start_response(
            "500 Internal Server Error",
            [("Content-Type", "text/html; charset=utf-8"), ("Content-Length", str(len(body)))],
        )
        return [body]


application = _flask_app
