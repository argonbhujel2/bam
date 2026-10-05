from flask import g, request
from app import db
from app.models import SiteSetting, AuditLog
from functools import wraps
from flask_login import current_user
from flask import abort


def get_setting(key, default="", lang=None):
    if lang is None:
        lang = getattr(g, "lang", "en")
    try:
        setting = SiteSetting.query.filter_by(key=key).first()
        if not setting:
            return default
        return setting.get_value(lang) or default
    except Exception:
        return default


def set_setting(key, value_en=None, value_ne=None, value_json=None, group="general"):
    setting = SiteSetting.query.filter_by(key=key).first()
    if not setting:
        setting = SiteSetting(key=key, group=group)
        db.session.add(setting)
    if value_en is not None:
        setting.value_en = value_en
    if value_ne is not None:
        setting.value_ne = value_ne
    if value_json is not None:
        setting.value_json = value_json
    db.session.commit()
    return setting


def log_audit(action, module, record_id=None, record_title=None, details=None):
    if not current_user.is_authenticated:
        return
    log = AuditLog(
        admin_user_id=current_user.id,
        action=action,
        module=module,
        record_id=record_id,
        record_title=record_title,
        details=details,
        ip_address=request.remote_addr,
    )
    db.session.add(log)
    db.session.commit()


def permission_required(permission_name):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(403)
            if not current_user.has_permission(permission_name):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def role_required(*role_names):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(403)
            if current_user.role and current_user.role.name == "Super Admin":
                return f(*args, **kwargs)
            if not any(current_user.has_role(r) for r in role_names):
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def t(en_text, ne_text=None):
    """Simple translation helper based on current language."""
    lang = getattr(g, "lang", "en")
    if lang == "ne" and ne_text:
        return ne_text
    return en_text
