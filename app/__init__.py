from flask import Flask, request, session, g
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import config_by_name
import os
import logging

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()
mail = Mail()
limiter = Limiter(key_func=get_remote_address, default_limits=[])

_log = logging.getLogger("bamstudio")


def create_app(config_name=None):
    """Application factory. Returns a Flask instance (never the `app` package)."""
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")

    # IMPORTANT: variable must NOT be named `app` — that collides with this package
    # name on some import paths and caused: AttributeError: module 'app' has no attribute 'config'
    _pkg_dir = os.path.dirname(os.path.abspath(__file__))
    flask_app = Flask(
        __name__,
        instance_relative_config=True,
        template_folder=os.path.join(_pkg_dir, "templates"),
        static_folder=os.path.join(_pkg_dir, "static"),
    )
    flask_app.config.from_object(
        config_by_name.get(config_name, config_by_name["default"])
    )

    # Vercel / serverless: /var/task is read-only
    if os.environ.get("VERCEL") or not os.access(
        os.path.dirname(flask_app.instance_path) or flask_app.instance_path, os.W_OK
    ):
        flask_app.instance_path = "/tmp/instance"
        try:
            os.makedirs(flask_app.instance_path, exist_ok=True)
        except OSError:
            pass

    db.init_app(flask_app)
    migrate.init_app(flask_app, db)
    login_manager.init_app(flask_app)
    csrf.init_app(flask_app)

    @flask_app.before_request
    def _ensure_session():
        session.permanent = True
        session.setdefault("_csrf_ready", True)

    mail.init_app(flask_app)
    limiter.init_app(flask_app)

    login_manager.login_view = "admin_auth.login"
    login_manager.login_message_category = "warning"
    login_manager.session_protection = "strong"

    @login_manager.user_loader
    def load_user(user_id):
        from app.models import AdminUser
        try:
            return AdminUser.query.get(int(user_id))
        except Exception:
            return None

    @flask_app.before_request
    def set_language():
        lang = request.args.get("lang") or request.cookies.get("lang") or session.get("lang")
        if lang not in ("en", "ne"):
            lang = flask_app.config.get("DEFAULT_LANGUAGE", "en")
        g.lang = lang
        session["lang"] = lang

    @flask_app.context_processor
    def inject_globals():
        lang = getattr(g, "lang", "en")
        nav_items = []
        site_name = "BAM Studio"
        site_tagline = (
            "Digital Experiences. Engineered."
            if lang == "en"
            else "डिजिटल अनुभव। ईन्जिनियर गरिएको।"
        )

        def safe_get_setting(key, default=""):
            try:
                from app.utils.helpers import get_setting
                return get_setting(key, default)
            except Exception:
                return default

        try:
            from app.models import NavigationItem
            nav_items = (
                NavigationItem.query.filter_by(is_active=True, parent_id=None)
                .order_by(NavigationItem.display_order)
                .all()
            )
            site_name = safe_get_setting("site_name", site_name)
            site_tagline = safe_get_setting("site_tagline", site_tagline)
        except Exception:
            pass

        return {
            "current_lang": lang,
            "nav_items": nav_items,
            "get_setting": safe_get_setting,
            "site_name": site_name,
            "site_tagline": site_tagline,
        }

    from app.routes.public import public_bp
    from app.routes.admin_auth import admin_auth_bp
    from app.routes.admin import admin_bp
    from app.routes.api import api_bp

    flask_app.register_blueprint(public_bp)
    flask_app.register_blueprint(admin_auth_bp, url_prefix="/admin")
    flask_app.register_blueprint(admin_bp, url_prefix="/admin")
    flask_app.register_blueprint(api_bp, url_prefix="/api")

    def _plain_error(code, title, message):
        html = (
            f"<!DOCTYPE html><html><head><meta charset=utf-8>"
            f"<title>{code} — BAM Studio</title>"
            f"<style>body{{font-family:system-ui;background:#0a0a0a;color:#eee;"
            f"display:flex;align-items:center;justify-content:center;min-height:100vh;margin:0}}"
            f".box{{text-align:center;padding:2rem}}.code{{font-size:4rem;opacity:.4}}"
            f"a{{color:#c9a227}}</style></head><body><div class=box>"
            f"<div class=code>{code}</div><h1>{title}</h1><p>{message}</p>"
            f"<p><a href=/>Go Home</a></p></div></body></html>"
        )
        return html, code

    @flask_app.errorhandler(404)
    def not_found(e):
        try:
            from flask import render_template
            return render_template("public/errors/404.html"), 404
        except Exception:
            return _plain_error(404, "Page not found", "The page does not exist.")

    @flask_app.errorhandler(403)
    def forbidden(e):
        try:
            from flask import render_template
            return render_template("public/errors/403.html"), 403
        except Exception:
            return _plain_error(403, "Forbidden", "You do not have access to this page.")

    @flask_app.errorhandler(500)
    def server_error(e):
        try:
            from flask import render_template
            return render_template("public/errors/500.html"), 500
        except Exception:
            return _plain_error(500, "Something went wrong", "Please try again later.")

    @flask_app.after_request
    def set_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response

    # Lightweight health check (no DB) for debugging deploys
    @flask_app.route("/health")
    def health():
        return {"status": "ok"}, 200

    # Auto-create tables + seed (never crash import)
    with flask_app.app_context():
        try:
            import app.models  # noqa: F401
            db.create_all()
            from app.models import Service
            from sqlalchemy.exc import IntegrityError

            need_seed = False
            try:
                need_seed = Service.query.count() == 0
            except Exception:
                need_seed = True

            if need_seed:
                try:
                    from app.services.seed import run_seed
                    run_seed()
                except IntegrityError:
                    db.session.rollback()
                except Exception as seed_exc:
                    db.session.rollback()
                    _log.warning("DB seed skipped or failed: %s", seed_exc)
        except Exception as exc:
            try:
                db.session.rollback()
            except Exception:
                pass
            _log.warning("DB init skipped or failed: %s", exc)

    return flask_app
