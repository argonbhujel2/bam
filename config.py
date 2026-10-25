import os
from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv

# Always load .env from project root (next to this file), not only CWD
_BASE = Path(__file__).resolve().parent
load_dotenv(_BASE / ".env")
load_dotenv()  # also allow CWD override


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-in-production")
    SQLALCHEMY_DATABASE_URI = (os.environ.get("DATABASE_URL") or "sqlite:///bamstudio.db").strip()
    # Postgres (Neon, Layerbase, etc.)
    if SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace(
            "postgres://", "postgresql://", 1
        )
    if SQLALCHEMY_DATABASE_URI.startswith("postgresql") and "sslmode=" not in SQLALCHEMY_DATABASE_URI:
        sep = "&" if "?" in SQLALCHEMY_DATABASE_URI else "?"
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI + sep + "sslmode=require"
    # Turso (libSQL) — set DATABASE_URL=libsql://<db>-<org>.turso.io?authToken=<token>
    # or TURSO_DATABASE_URL + TURSO_AUTH_TOKEN
    _turso = (os.environ.get("TURSO_DATABASE_URL") or "").strip()
    _turso_token = (os.environ.get("TURSO_AUTH_TOKEN") or "").strip()
    if _turso:
        # Accept libsql://host or https://host.turso.io
        host = (
            _turso.replace("libsql://", "")
            .replace("https://", "")
            .split("?")[0]
            .split("/")[0]
        )
        SQLALCHEMY_DATABASE_URI = f"sqlite+libsql://{host}?secure=true"
        token = _turso_token
        if "authToken=" in _turso:
            # extract token from URL if present
            for part in _turso.split("?", 1)[-1].split("&"):
                if part.startswith("authToken="):
                    token = part.split("=", 1)[-1]
                    break
        if token:
            SQLALCHEMY_DATABASE_URI += f"&authToken={token}"
    elif SQLALCHEMY_DATABASE_URI.startswith("libsql://"):
        host_part = SQLALCHEMY_DATABASE_URI[len("libsql://") :]
        SQLALCHEMY_DATABASE_URI = "sqlite+libsql://" + host_part
        if "secure=" not in SQLALCHEMY_DATABASE_URI:
            SQLALCHEMY_DATABASE_URI += (
                "&" if "?" in SQLALCHEMY_DATABASE_URI else "?"
            ) + "secure=true"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }

    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "False") == "True"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_PATH = "/"
    SESSION_COOKIE_NAME = "bam_session"
    REMEMBER_COOKIE_DURATION = timedelta(days=14)
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = SESSION_COOKIE_SECURE

    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif", "svg", "pdf"}
    ALLOWED_IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "gif"}
    ALLOWED_CV_EXTENSIONS = {"pdf", "doc", "docx"}

    CLOUDINARY_CLOUD_NAME = os.environ.get("CLOUDINARY_CLOUD_NAME")
    CLOUDINARY_API_KEY = os.environ.get("CLOUDINARY_API_KEY")
    CLOUDINARY_API_SECRET = os.environ.get("CLOUDINARY_API_SECRET")

    # Mail (Flask-Mail)
    MAIL_SERVER = (os.environ.get("MAIL_SERVER") or "").strip() or None
    MAIL_PORT = int(os.environ.get("MAIL_PORT") or 587)
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "True").strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    )
    MAIL_USE_SSL = os.environ.get("MAIL_USE_SSL", "False").strip().lower() in (
        "1",
        "true",
        "yes",
        "on",
    )
    MAIL_USERNAME = (os.environ.get("MAIL_USERNAME") or "").strip() or None
    MAIL_PASSWORD = (os.environ.get("MAIL_PASSWORD") or "").strip() or None
    MAIL_DEFAULT_SENDER = (
        os.environ.get("MAIL_DEFAULT_SENDER") or "noreply@bamstudio.com"
    ).strip()
    # Optional: where notifications are delivered (defaults to MAIL_DEFAULT_SENDER)
    MAIL_NOTIFY_TO = (os.environ.get("MAIL_NOTIFY_TO") or "").strip() or None

    # Normalize SMTP: port 465 → SSL, port 587 → TLS
    if MAIL_PORT == 465 and not MAIL_USE_SSL:
        MAIL_USE_SSL = True
        MAIL_USE_TLS = False
    elif MAIL_PORT == 587 and not MAIL_USE_TLS and not MAIL_USE_SSL:
        MAIL_USE_TLS = True

    ADMIN_SETUP_SECRET = os.environ.get("ADMIN_SETUP_SECRET", "")

    SITE_URL = os.environ.get("SITE_URL", "http://localhost:5000")
    SITE_NAME = "BAM Studio"

    RATELIMIT_STORAGE_URI = os.environ.get("RATELIMIT_STORAGE_URI", "memory://")
    RATELIMIT_DEFAULT = "200 per day;50 per hour"

    LANGUAGES = ["en", "ne"]
    DEFAULT_LANGUAGE = "en"


class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    # On Vercel the filesystem is read-only; SQLite file paths will fail.
    # Always set DATABASE_URL to a Postgres (e.g. Neon) connection string.


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False


config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
