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

        def safe_get_setting(key, default="", lang=None, **kwargs):
            try:
                from app.utils.helpers import get_setting
                return get_setting(key, default, lang=lang)
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

    @flask_app.route("/debug-paths")
    def debug_paths():
        import os
        from pathlib import Path
        tpl = Path(flask_app.template_folder or "")
        st = Path(flask_app.static_folder or "")
        return {
            "template_folder": str(tpl),
            "template_exists": tpl.exists(),
            "home_html": str(tpl / "public" / "home.html"),
            "home_html_exists": (tpl / "public" / "home.html").exists(),
            "static_folder": str(st),
            "static_exists": st.exists(),
            "pkg_dir": str(Path(__file__).resolve().parent),
            "cwd": os.getcwd(),
            "listdir_pkg": sorted(os.listdir(Path(__file__).resolve().parent))[:50],
            "listdir_templates": (
                sorted(os.listdir(tpl)) if tpl.exists() else "MISSING"
            ),
        }

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
            # Always clean duplicate tech chips from concurrent seeds
            try:
                from app.services.seed import dedupe_tech_items
                dedupe_tech_items()
            except Exception:
                pass
            # Repair hero_heading if English field was saved with Nepali text
            try:
                from app.models import SiteSetting
                from app import db as _db
                import re
                _devanagari = re.compile(r"[\u0900-\u097F]")
                hh = SiteSetting.query.filter_by(key="hero_heading").first()
                if hh:
                    en = (hh.value_en or "").strip()
                    ne = (hh.value_ne or "").strip()
                    if en and _devanagari.search(en) and (not ne or ne == en):
                        # EN field has Nepali — move to NE, restore English default
                        hh.value_ne = en
                        hh.value_en = "WE BUILD DIGITAL EXPERIENCES."
                        _db.session.commit()
                    elif en and _devanagari.search(en) and ne and not _devanagari.search(ne):
                        # EN and NE swapped
                        hh.value_en, hh.value_ne = ne, en
                        _db.session.commit()
                hd = SiteSetting.query.filter_by(key="hero_desc").first()
                if hd:
                    en = (hd.value_en or "").strip()
                    ne = (hd.value_ne or "").strip()
                    if en and _devanagari.search(en) and (not ne or ne == en):
                        hd.value_ne = en
                        hd.value_en = "Websites, systems and digital solutions engineered for modern businesses."
                        _db.session.commit()
                    elif en and _devanagari.search(en) and ne and not _devanagari.search(ne):
                        hd.value_en, hd.value_ne = ne, en
                        _db.session.commit()
            except Exception:
                try:
                    from app import db as _db
                    _db.session.rollback()
                except Exception:
                    pass
            # Ensure SEO keywords setting exists (updates empty only)
            try:
                from app.models import SiteSetting
                from app import db as _db
                _kw = (
                    "BAM Studio, BAM Studio Nepal, BAM Studio Urlabari, "
                    "Web Development Company Nepal, Web Development Company Morang, "
                    "Website Development Nepal, Website Design Nepal, Web Designer Nepal, "
                    "Full Stack Developer Nepal, Custom Website Development Nepal, "
                    "Web Development in Urlabari, Website Design in Urlabari, "
                    "Web Development in Morang, Website Developer in Morang, "
                    "Web Development in Damak, Website Design in Damak, "
                    "Web Development in Pathari, Web Developer in Jhapa, "
                    "Custom Web Development, Hotel Management System Nepal, "
                    "Football Website Development Nepal, Event Ticketing Website, "
                    "School Website Development Nepal, UI/UX Design Nepal, "
                    "Flask Web Development, Python Web Development, "
                    "नेपालमा वेबसाइट बनाउने कम्पनी, वेबसाइट डिजाइन नेपाल, "
                    "उर्लाबारीमा वेबसाइट बनाउने, मोरङमा वेबसाइट डेभलपर, "
                    "होटल म्यानेजमेन्ट सिस्टम, QR मेनु सिस्टम"
                )
                s = SiteSetting.query.filter_by(key="seo_keywords").first()
                if not s:
                    _db.session.add(SiteSetting(key="seo_keywords", value_en=_kw, group="seo"))
                    _db.session.commit()
                elif not (s.value_en or "").strip():
                    s.value_en = _kw
                    _db.session.commit()
            except Exception:
                try:
                    from app import db as _db
                    _db.session.rollback()
                except Exception:
                    pass
        except Exception as exc:
            try:
                db.session.rollback()
            except Exception:
                pass
            _log.warning("DB init skipped or failed: %s", exc)

    return flask_app
