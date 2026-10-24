from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    current_app,
)
from flask_login import login_user, logout_user, login_required, current_user
from app import db, limiter
from app.models import AdminUser, Role, Permission
from app.utils.helpers import log_audit
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional
from datetime import datetime
from sqlalchemy import or_

admin_auth_bp = Blueprint("admin_auth", __name__)


class LoginForm(FlaskForm):
    email = StringField("Email or Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Sign In")


class SetupForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=80)])
    full_name = StringField("Full Name", validators=[Optional()])
    password = PasswordField(
        "Password", validators=[DataRequired(), Length(min=8)]
    )
    password2 = PasswordField(
        "Confirm Password",
        validators=[DataRequired(), EqualTo("password", message="Passwords must match")],
    )
    setup_secret = StringField("Setup Secret", validators=[DataRequired()])
    submit = SubmitField("Create Admin")


@admin_auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("10 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for("admin.dashboard"))
    form = LoginForm()
    if form.validate_on_submit():
        login_id = form.email.data.strip()
        user = AdminUser.query.filter(
            or_(AdminUser.email == login_id.lower(), AdminUser.username == login_id)
        ).first()
        if user and user.is_active and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            user.last_login = datetime.utcnow()
            db.session.commit()
            log_audit("login", "auth", details=f"User {user.email} logged in")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("admin.dashboard"))
        flash("Invalid email/username or password.", "error")
    return render_template("admin/login.html", form=form)


@admin_auth_bp.route("/logout")
@login_required
def logout():
    log_audit("logout", "auth", details=f"User {current_user.email} logged out")
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("admin_auth.login"))


@admin_auth_bp.route("/setup", methods=["GET", "POST"])
@limiter.limit("5 per hour")
def setup():
    """One-time admin bootstrap. Disabled after first Super Admin exists."""
    existing = AdminUser.query.first()
    if existing:
        flash("Setup is disabled. An admin already exists.", "error")
        return redirect(url_for("admin_auth.login"))

    form = SetupForm()
    if form.validate_on_submit():
        secret = current_app.config.get("ADMIN_SETUP_SECRET", "")
        if not secret or form.setup_secret.data != secret:
            flash("Invalid setup secret.", "error")
            return render_template("admin/setup.html", form=form)

        # Ensure Super Admin role + permissions exist
        role = Role.query.filter_by(name="Super Admin").first()
        if not role:
            role = Role(name="Super Admin", description="Full access")
            db.session.add(role)
            db.session.flush()

        user = AdminUser(
            email=form.email.data.strip().lower(),
            username=form.username.data.strip(),
            full_name=form.full_name.data,
            role_id=role.id,
            is_active=True,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Admin account created. Please log in.", "success")
        return redirect(url_for("admin_auth.login"))

    return render_template("admin/setup.html", form=form)
