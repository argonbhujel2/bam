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

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()
mail = Mail()
limiter = Limiter(key_func=get_remote_address, default_limits=[])


def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get("FLASK_ENV", "development")
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_by_name.get(config_name, config_by_name["default"]))

    # Vercel / serverless: /var/task is read-only. Flask-SQLAlchemy calls
    # os.makedirs(app.instance_path) during init_app, which fails with
    # OSError: [Errno 30] Read-only file system. Point instance_path at /tmp.
    if os.environ.get("VERCEL") or not os.access(
        os.path.dirname(app.instance_path) or app.instance_path, os.W_OK
    ):
        app.instance_path = "/tmp/instance"
        try:
            os.makedirs(app.instance_path, exist_ok=True)
        except OSError:
            pass

    # Init extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Ensure session exists so CSRF token can be stored (fixes "CSRF session token is missing")
    @app.before_request
    def _ensure_session():
        from flask import session
        session.permanent = True
        session.setdefault("_csrf_ready", True)
    mail.init_app(app)
    limiter.init_app(app)

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

    # Language handling
    @app.before_request
    def set_language():
        lang = request.args.get("lang") or request.cookies.get("lang") or session.get("lang")
        if lang not in ("en", "ne"):
            lang = app.config.get("DEFAULT_LANGUAGE", "en")
        g.lang = lang
        session["lang"] = lang

    # Context processors — resilient if tables are missing / DB is empty
    @app.context_processor
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

    # Register blueprints
    from app.routes.public import public_bp
    from app.routes.admin_auth import admin_auth_bp
    from app.routes.admin import admin_bp
    from app.routes.api import api_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(admin_auth_bp, url_prefix="/admin")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(api_bp, url_prefix="/api")

    # Error handlers with plain-HTML fallback (avoids TemplateNotFound cascades)
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

    @app.errorhandler(404)
    def not_found(e):
        try:
            from flask import render_template
            return render_template("public/errors/404.html"), 404
        except Exception:
            return _plain_error(404, "Page not found", "The page you\'re looking for doesn\'t exist.")

    @app.errorhandler(403)
    def forbidden(e):
        try:
            from flask import render_template
            return render_template("public/errors/403.html"), 403
        except Exception:
            return _plain_error(403, "Forbidden", "You do not have access to this page.")

    @app.errorhandler(500)
    def server_error(e):
        try:
            from flask import render_template
            return render_template("public/errors/500.html"), 500
        except Exception:
            return _plain_error(500, "Something went wrong", "Please try again later.")

    # Security headers
    @app.after_request
    def set_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response

    # Auto-create tables + seed if missing (needed on Vercel / first deploy).
    # Must never raise — concurrent cold starts can race on unique constraints.
    with app.app_context():
        try:
            import logging
            import app.models  # noqa: F401 — register models on metadata
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
                    # Another concurrent instance already seeded
                    db.session.rollback()
                except Exception as seed_exc:
                    db.session.rollback()
                    logging.getLogger("bamstudio").warning(
                        "DB seed skipped or failed: %s", seed_exc
                    )
        except Exception as exc:
            try:
                db.session.rollback()
            except Exception:
                pass
            import logging
            logging.getLogger("bamstudio").warning(
                "DB init skipped or failed: %s", exc
            )

    return app
