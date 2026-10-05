from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    abort,
    current_app,
)
from flask_login import login_required, current_user
from app import db
from app.models import (
    Project,
    ProjectCategory,
    ProjectImage,
    Service,
    ProcessStep,
    Career,
    CareerApplication,
    ContactInquiry,
    ProjectInquiry,
    TeamMember,
    Media,
    SiteSetting,
    NavigationItem,
    AdminUser,
    Role,
    AuditLog,
)
from app.utils.helpers import log_audit, permission_required, get_setting, set_setting
from app.utils.email import notify_status_update
from app.utils.media import (
    upload_to_cloudinary,
    save_media_record,
    allowed_file,
    delete_from_cloudinary,
)
from datetime import datetime, timedelta
from sqlalchemy import func

admin_bp = Blueprint("admin", __name__)


def admin_required(f):
    from functools import wraps
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if not current_user.is_active:
            abort(403)
        return f(*args, **kwargs)
    return decorated


# ── Dashboard ──────────────────────────────────────────────────────────
@admin_bp.route("/")
@admin_required
def dashboard():
    stats = {
        "total_projects": Project.query.count(),
        "published_projects": Project.query.filter_by(is_published=True).count(),
        "active_services": Service.query.filter_by(is_active=True).count(),
        "open_careers": Career.query.filter_by(status="open").count(),
        "new_applications": CareerApplication.query.filter_by(status="new").count(),
        "new_inquiries": ProjectInquiry.query.filter_by(status="new").count()
        + ContactInquiry.query.filter_by(status="new").count(),
    }
    recent_applications = (
        CareerApplication.query.order_by(CareerApplication.created_at.desc())
        .limit(5)
        .all()
    )
    recent_inquiries = (
        ProjectInquiry.query.order_by(ProjectInquiry.created_at.desc()).limit(5).all()
    )
    recent_projects = (
        Project.query.order_by(Project.updated_at.desc()).limit(5).all()
    )
    recent_audit = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(10).all()
    return render_template(
        "admin/dashboard.html",
        stats=stats,
        recent_applications=recent_applications,
        recent_inquiries=recent_inquiries,
        recent_projects=recent_projects,
        recent_audit=recent_audit,
    )


# ── Projects ───────────────────────────────────────────────────────────
@admin_bp.route("/projects")
@admin_required
def projects():
    page = request.args.get("page", 1, type=int)
    q = request.args.get("q", "")
    query = Project.query
    if q:
        query = query.filter(Project.title.ilike(f"%{q}%"))
    pagination = query.order_by(Project.display_order, Project.created_at.desc()).paginate(
        page=page, per_page=15, error_out=False
    )
    return render_template(
        "admin/projects/list.html", pagination=pagination, q=q
    )


@admin_bp.route("/projects/new", methods=["GET", "POST"])
@admin_required
def project_new():
    categories = ProjectCategory.query.order_by(ProjectCategory.display_order).all()
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        if not title:
            flash("Title is required.", "error")
            return render_template("admin/projects/form.html", project=None, categories=categories)
        slug = request.form.get("slug") or Project.generate_slug(title)
        if Project.query.filter_by(slug=slug).first():
            slug = f"{slug}-{int(datetime.utcnow().timestamp())}"
        project = Project(
            title=title,
            slug=slug,
            description_en=request.form.get("description_en"),
            description_ne=request.form.get("description_ne"),
            full_description_en=request.form.get("full_description_en"),
            full_description_ne=request.form.get("full_description_ne"),
            challenge_en=request.form.get("challenge_en"),
            challenge_ne=request.form.get("challenge_ne"),
            solution_en=request.form.get("solution_en"),
            solution_ne=request.form.get("solution_ne"),
            features_en=request.form.get("features_en"),
            features_ne=request.form.get("features_ne"),
            client=request.form.get("client"),
            location=request.form.get("location"),
            technologies=[t.strip() for t in request.form.get("technologies", "").split(",") if t.strip()],
            live_url=request.form.get("live_url"),
            github_url=request.form.get("github_url"),
            project_year=request.form.get("project_year"),
            status=request.form.get("status") or "Completed",
            result_en=request.form.get("result_en"),
            result_ne=request.form.get("result_ne"),
            category_id=request.form.get("category_id") or None,
            is_featured=bool(request.form.get("is_featured")),
            is_published=bool(request.form.get("is_published")),
            display_order=int(request.form.get("display_order") or 0),
        )
        if "cover_image" in request.files and request.files["cover_image"].filename:
            result = upload_to_cloudinary(request.files["cover_image"], folder="bamstudio/projects")
            if result:
                project.cover_image = result.get("secure_url")
        db.session.add(project)
        db.session.commit()
        log_audit("created", "project", project.id, project.title)
        flash("Project created.", "success")
        return redirect(url_for("admin.projects"))
    return render_template("admin/projects/form.html", project=None, categories=categories)


@admin_bp.route("/projects/<int:id>/edit", methods=["GET", "POST"])
@admin_required
def project_edit(id):
    project = Project.query.get_or_404(id)
    categories = ProjectCategory.query.order_by(ProjectCategory.display_order).all()
    if request.method == "POST":
        project.title = request.form.get("title", "").strip() or project.title
        project.slug = request.form.get("slug") or project.slug
        project.description_en = request.form.get("description_en")
        project.description_ne = request.form.get("description_ne")
        project.full_description_en = request.form.get("full_description_en")
        project.full_description_ne = request.form.get("full_description_ne")
        project.challenge_en = request.form.get("challenge_en")
        project.challenge_ne = request.form.get("challenge_ne")
        project.solution_en = request.form.get("solution_en")
        project.solution_ne = request.form.get("solution_ne")
        project.features_en = request.form.get("features_en")
        project.features_ne = request.form.get("features_ne")
        project.client = request.form.get("client")
        project.location = request.form.get("location")
        project.technologies = [t.strip() for t in request.form.get("technologies", "").split(",") if t.strip()]
        project.live_url = request.form.get("live_url")
        project.github_url = request.form.get("github_url")
        project.project_year = request.form.get("project_year")
        project.status = request.form.get("status") or project.status
        project.result_en = request.form.get("result_en")
        project.result_ne = request.form.get("result_ne")
        project.category_id = request.form.get("category_id") or None
        project.is_featured = bool(request.form.get("is_featured"))
        project.is_published = bool(request.form.get("is_published"))
        project.display_order = int(request.form.get("display_order") or 0)
        if "cover_image" in request.files and request.files["cover_image"].filename:
            result = upload_to_cloudinary(request.files["cover_image"], folder="bamstudio/projects")
            if result:
                project.cover_image = result.get("secure_url")
        db.session.commit()
        log_audit("updated", "project", project.id, project.title)
        flash("Project updated.", "success")
        return redirect(url_for("admin.projects"))
    return render_template("admin/projects/form.html", project=project, categories=categories)


@admin_bp.route("/projects/<int:id>/delete", methods=["POST"])
@admin_required
def project_delete(id):
    project = Project.query.get_or_404(id)
    title = project.title
    db.session.delete(project)
    db.session.commit()
    log_audit("deleted", "project", id, title)
    flash("Project deleted.", "success")
    return redirect(url_for("admin.projects"))


# ── Categories ─────────────────────────────────────────────────────────
@admin_bp.route("/categories", methods=["GET", "POST"])
@admin_required
def categories():
    if request.method == "POST":
        name_en = request.form.get("name_en", "").strip()
        if name_en:
            from slugify import slugify
            cat = ProjectCategory(
                name_en=name_en,
                name_ne=request.form.get("name_ne"),
                slug=slugify(name_en),
                display_order=int(request.form.get("display_order") or 0),
            )
            db.session.add(cat)
            db.session.commit()
            flash("Category added.", "success")
        return redirect(url_for("admin.categories"))
    cats = ProjectCategory.query.order_by(ProjectCategory.display_order).all()
    return render_template("admin/categories.html", categories=cats)


# ── Services ───────────────────────────────────────────────────────────
@admin_bp.route("/services")
@admin_required
def services():
    items = Service.query.order_by(Service.display_order).all()
    return render_template("admin/services/list.html", services=items)


@admin_bp.route("/services/new", methods=["GET", "POST"])
@admin_required
def service_new():
    if request.method == "POST":
        image_url = (request.form.get("image_url") or "").strip() or None
        if "image" in request.files and request.files["image"].filename:
            result = upload_to_cloudinary(request.files["image"], folder="bamstudio/services")
            if result:
                image_url = result.get("secure_url") or result.get("url")
        s = Service(
            number=request.form.get("number", "01"),
            title_en=request.form.get("title_en", "").strip(),
            title_ne=request.form.get("title_ne"),
            description_en=request.form.get("description_en"),
            description_ne=request.form.get("description_ne"),
            detail_en=request.form.get("detail_en"),
            detail_ne=request.form.get("detail_ne"),
            image=image_url,
            is_active=bool(request.form.get("is_active")),
            is_featured=bool(request.form.get("is_featured")),
            display_order=int(request.form.get("display_order") or 0),
        )
        db.session.add(s)
        db.session.commit()
        log_audit("created", "service", s.id, s.title_en)
        flash("Service created.", "success")
        return redirect(url_for("admin.services"))
    return render_template("admin/services/form.html", service=None)


@admin_bp.route("/services/<int:id>/edit", methods=["GET", "POST"])
@admin_required
def service_edit(id):
    s = Service.query.get_or_404(id)
    if request.method == "POST":
        s.number = request.form.get("number", s.number)
        s.title_en = request.form.get("title_en", "").strip() or s.title_en
        s.title_ne = request.form.get("title_ne")
        s.description_en = request.form.get("description_en")
        s.description_ne = request.form.get("description_ne")
        s.detail_en = request.form.get("detail_en")
        s.detail_ne = request.form.get("detail_ne")
        s.is_active = bool(request.form.get("is_active"))
        s.is_featured = bool(request.form.get("is_featured"))
        s.display_order = int(request.form.get("display_order") or 0)
        if request.form.get("image_url"):
            s.image = request.form.get("image_url").strip()
        if "image" in request.files and request.files["image"].filename:
            result = upload_to_cloudinary(request.files["image"], folder="bamstudio/services")
            if result:
                s.image = result.get("secure_url") or result.get("url")
        db.session.commit()
        log_audit("updated", "service", s.id, s.title_en)
        flash("Service updated.", "success")
        return redirect(url_for("admin.services"))
    return render_template("admin/services/form.html", service=s)


@admin_bp.route("/services/<int:id>/delete", methods=["POST"])
@admin_required
def service_delete(id):
    s = Service.query.get_or_404(id)
    title = s.title_en
    db.session.delete(s)
    db.session.commit()
    log_audit("deleted", "service", id, title)
    flash("Service deleted.", "success")
    return redirect(url_for("admin.services"))


# ── Process Steps ──────────────────────────────────────────────────────
@admin_bp.route("/process", methods=["GET", "POST"])
@admin_required
def process_steps():
    if request.method == "POST":
        step = ProcessStep(
            number=request.form.get("number", "01"),
            title_en=request.form.get("title_en", "").strip(),
            title_ne=request.form.get("title_ne"),
            description_en=request.form.get("description_en"),
            description_ne=request.form.get("description_ne"),
            display_order=int(request.form.get("display_order") or 0),
            is_active=True,
        )
        db.session.add(step)
        db.session.commit()
        flash("Process step added.", "success")
        return redirect(url_for("admin.process_steps"))
    steps = ProcessStep.query.order_by(ProcessStep.display_order).all()
    return render_template("admin/process.html", steps=steps)


# ── Careers ────────────────────────────────────────────────────────────
@admin_bp.route("/careers")
@admin_required
def careers():
    items = Career.query.order_by(Career.display_order, Career.created_at.desc()).all()
    return render_template("admin/careers/list.html", careers=items)


@admin_bp.route("/careers/new", methods=["GET", "POST"])
@admin_required
def career_new():
    if request.method == "POST":
        title_en = request.form.get("title_en", "").strip()
        from slugify import slugify
        c = Career(
            title_en=title_en,
            title_ne=request.form.get("title_ne"),
            slug=slugify(title_en),
            department=request.form.get("department"),
            location=request.form.get("location", "Remote / Nepal"),
            employment_type=request.form.get("employment_type", "Full-time"),
            experience=request.form.get("experience"),
            salary_range=request.form.get("salary_range"),
            description_en=request.form.get("description_en"),
            description_ne=request.form.get("description_ne"),
            responsibilities_en=request.form.get("responsibilities_en"),
            responsibilities_ne=request.form.get("responsibilities_ne"),
            requirements_en=request.form.get("requirements_en"),
            requirements_ne=request.form.get("requirements_ne"),
            skills=[s.strip() for s in request.form.get("skills", "").split(",") if s.strip()],
            status=request.form.get("status", "draft"),
            display_order=int(request.form.get("display_order") or 0),
        )
        deadline = request.form.get("deadline")
        if deadline:
            try:
                c.deadline = datetime.strptime(deadline, "%Y-%m-%d").date()
            except ValueError:
                pass
        db.session.add(c)
        db.session.commit()
        log_audit("created", "career", c.id, c.title_en)
        flash("Vacancy created.", "success")
        return redirect(url_for("admin.careers"))
    return render_template("admin/careers/form.html", career=None)


@admin_bp.route("/careers/<int:id>/edit", methods=["GET", "POST"])
@admin_required
def career_edit(id):
    c = Career.query.get_or_404(id)
    if request.method == "POST":
        c.title_en = request.form.get("title_en", "").strip() or c.title_en
        c.title_ne = request.form.get("title_ne")
        c.department = request.form.get("department")
        c.location = request.form.get("location")
        c.employment_type = request.form.get("employment_type")
        c.experience = request.form.get("experience")
        c.salary_range = request.form.get("salary_range")
        c.description_en = request.form.get("description_en")
        c.description_ne = request.form.get("description_ne")
        c.responsibilities_en = request.form.get("responsibilities_en")
        c.responsibilities_ne = request.form.get("responsibilities_ne")
        c.requirements_en = request.form.get("requirements_en")
        c.requirements_ne = request.form.get("requirements_ne")
        c.skills = [s.strip() for s in request.form.get("skills", "").split(",") if s.strip()]
        c.status = request.form.get("status", c.status)
        c.display_order = int(request.form.get("display_order") or 0)
        deadline = request.form.get("deadline")
        if deadline:
            try:
                c.deadline = datetime.strptime(deadline, "%Y-%m-%d").date()
            except ValueError:
                pass
        db.session.commit()
        log_audit("updated", "career", c.id, c.title_en)
        flash("Vacancy updated.", "success")
        return redirect(url_for("admin.careers"))
    return render_template("admin/careers/form.html", career=c)


@admin_bp.route("/careers/<int:id>/delete", methods=["POST"])
@admin_required
def career_delete(id):
    c = Career.query.get_or_404(id)
    title = c.title_en
    db.session.delete(c)
    db.session.commit()
    log_audit("deleted", "career", id, title)
    flash("Vacancy deleted.", "success")
    return redirect(url_for("admin.careers"))


# ── Applications ───────────────────────────────────────────────────────
@admin_bp.route("/applications")
@admin_required
def applications():
    status = request.args.get("status", "")
    q = request.args.get("q", "")
    query = CareerApplication.query
    if status:
        query = query.filter_by(status=status)
    if q:
        query = query.filter(
            (CareerApplication.full_name.ilike(f"%{q}%"))
            | (CareerApplication.email.ilike(f"%{q}%"))
        )
    page = request.args.get("page", 1, type=int)
    pagination = query.order_by(CareerApplication.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    return render_template(
        "admin/applications/list.html", pagination=pagination, status=status, q=q
    )


@admin_bp.route("/applications/<int:id>", methods=["GET", "POST"])
@admin_required
def application_detail(id):
    app = CareerApplication.query.get_or_404(id)
    if request.method == "POST":
        old = app.status
        app.status = request.form.get("status", app.status)
        app.internal_notes = request.form.get("internal_notes")
        db.session.commit()
        log_audit("updated", "application", app.id, app.full_name)
        try:
            notify_status_update("application", app.full_name, app.email, old, app.status)
        except Exception:
            pass
        flash("Application updated.", "success")
        return redirect(url_for("admin.application_detail", id=id))
    return render_template("admin/applications/detail.html", application=app)


# ── Inquiries ──────────────────────────────────────────────────────────
@admin_bp.route("/inquiries")
@admin_required
def inquiries():
    tab = request.args.get("tab", "project")
    if tab == "contact":
        items = ContactInquiry.query.order_by(ContactInquiry.created_at.desc()).all()
    else:
        items = ProjectInquiry.query.order_by(ProjectInquiry.created_at.desc()).all()
    return render_template("admin/inquiries/list.html", items=items, tab=tab)


@admin_bp.route("/inquiries/project/<int:id>", methods=["GET", "POST"])
@admin_required
def inquiry_project_detail(id):
    item = ProjectInquiry.query.get_or_404(id)
    if request.method == "POST":
        old = item.status
        item.status = request.form.get("status", item.status)
        item.internal_notes = request.form.get("internal_notes")
        db.session.commit()
        try:
            notify_status_update("inquiry", item.name, item.email, old, item.status)
        except Exception:
            pass
        flash("Updated.", "success")
        return redirect(url_for("admin.inquiry_project_detail", id=id))
    return render_template("admin/inquiries/detail.html", item=item, kind="project")


@admin_bp.route("/inquiries/contact/<int:id>", methods=["GET", "POST"])
@admin_required
def inquiry_contact_detail(id):
    item = ContactInquiry.query.get_or_404(id)
    if request.method == "POST":
        old = item.status
        item.status = request.form.get("status", item.status)
        item.internal_notes = request.form.get("internal_notes")
        db.session.commit()
        try:
            notify_status_update("contact", item.name, item.email, old, item.status)
        except Exception:
            pass
        flash("Updated.", "success")
        return redirect(url_for("admin.inquiry_contact_detail", id=id))
    return render_template("admin/inquiries/detail.html", item=item, kind="contact")


# ── Settings ───────────────────────────────────────────────────────────
@admin_bp.route("/settings", methods=["GET", "POST"])
@admin_required
def settings():
    if request.method == "POST":
        keys = [
            "site_name",
            "site_tagline",
            "email",
            "phone",
            "address",
            "hero_heading_en",
            "hero_heading_ne",
            "hero_desc_en",
            "hero_desc_ne",
            "footer_description",
            "copyright",
            "facebook",
            "instagram",
            "linkedin",
            "github",
            "youtube",
            "seo_default_title",
            "seo_default_description",
        ]
        keys = list(keys) + ["site_logo", "site_favicon", "hero_bg_image"]
        for key in keys:
            val = request.form.get(key)
            if val is not None:
                if key.endswith("_en"):
                    base = key[:-3]
                    set_setting(base, value_en=val)
                elif key.endswith("_ne"):
                    base = key[:-3]
                    set_setting(base, value_ne=val)
                else:
                    set_setting(key, value_en=val)
        # File pickers for logo / favicon / hero
        for field, setting_key, folder in (
            ("logo_file", "site_logo", "bamstudio/brand"),
            ("favicon_file", "site_favicon", "bamstudio/brand"),
            ("hero_bg_file", "hero_bg_image", "bamstudio/hero"),
        ):
            if field in request.files and request.files[field].filename:
                result = upload_to_cloudinary(request.files[field], folder=folder)
                if result:
                    url = result.get("secure_url") or result.get("url")
                    set_setting(setting_key, value_en=url)
                    save_media_record(result, request.files[field].filename, uploaded_by=current_user.id)
        flash("Settings saved.", "success")
        return redirect(url_for("admin.settings"))
    return render_template("admin/settings.html")


# ── Media ──────────────────────────────────────────────────────────────
@admin_bp.route("/media", methods=["GET", "POST"])
@admin_required
def media():
    if request.method == "POST" and "file" in request.files:
        f = request.files["file"]
        if f and f.filename and allowed_file(f.filename):
            result = upload_to_cloudinary(f, folder="bamstudio/media")
            if result:
                save_media_record(
                    result,
                    f.filename,
                    uploaded_by=current_user.id,
                    alt_text=request.form.get("alt_text"),
                )
                flash("File uploaded.", "success")
            else:
                flash("Upload failed.", "error")
        return redirect(url_for("admin.media"))
    page = request.args.get("page", 1, type=int)
    pagination = Media.query.order_by(Media.created_at.desc()).paginate(
        page=page, per_page=24, error_out=False
    )
    return render_template("admin/media.html", pagination=pagination)


# ── Analytics ──────────────────────────────────────────────────────────
@admin_bp.route("/analytics")
@admin_required
def analytics():
    now = datetime.utcnow()
    months = []
    inquiry_counts = []
    app_counts = []
    for i in range(5, -1, -1):
        start = (now.replace(day=1) - timedelta(days=30 * i)).replace(day=1)
        end = (start + timedelta(days=32)).replace(day=1)
        months.append(start.strftime("%b %Y"))
        inquiry_counts.append(
            ProjectInquiry.query.filter(
                ProjectInquiry.created_at >= start, ProjectInquiry.created_at < end
            ).count()
            + ContactInquiry.query.filter(
                ContactInquiry.created_at >= start, ContactInquiry.created_at < end
            ).count()
        )
        app_counts.append(
            CareerApplication.query.filter(
                CareerApplication.created_at >= start,
                CareerApplication.created_at < end,
            ).count()
        )
    data = {
        "total_inquiries": ProjectInquiry.query.count() + ContactInquiry.query.count(),
        "total_applications": CareerApplication.query.count(),
        "total_projects": Project.query.count(),
        "open_vacancies": Career.query.filter_by(status="open").count(),
        "months": months,
        "inquiry_counts": inquiry_counts,
        "app_counts": app_counts,
    }
    return render_template("admin/analytics.html", data=data)


# ── Audit Logs ─────────────────────────────────────────────────────────
@admin_bp.route("/audit")
@admin_required
def audit_logs():
    page = request.args.get("page", 1, type=int)
    pagination = AuditLog.query.order_by(AuditLog.created_at.desc()).paginate(
        page=page, per_page=30, error_out=False
    )
    return render_template("admin/audit.html", pagination=pagination)


# ── Users ──────────────────────────────────────────────────────────────
@admin_bp.route("/users", methods=["GET", "POST"])
@admin_required
def users():
    if not current_user.has_role("Super Admin"):
        abort(403)
    if request.method == "POST":
        email = (request.form.get("email") or "").strip().lower()
        username = (request.form.get("username") or "").strip()
        password = request.form.get("password") or ""
        full_name = (request.form.get("full_name") or "").strip()
        role_id = request.form.get("role_id", type=int)
        if not email or not username or not password:
            flash("Email, username and password are required.", "error")
            return redirect(url_for("admin.users"))
        if AdminUser.query.filter(
            (AdminUser.email == email) | (AdminUser.username == username)
        ).first():
            flash("Email or username already exists.", "error")
            return redirect(url_for("admin.users"))
        role = Role.query.get(role_id) if role_id else Role.query.filter_by(name="Editor").first()
        user = AdminUser(
            email=email,
            username=username,
            full_name=full_name or username,
            role_id=role.id if role else None,
            is_active=True,
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash("User created.", "success")
        return redirect(url_for("admin.users"))
    users_list = AdminUser.query.order_by(AdminUser.created_at.desc()).all()
    roles = Role.query.all()
    return render_template("admin/users.html", users=users_list, roles=roles)


@admin_bp.route("/users/<int:id>/toggle", methods=["POST"])
@admin_required
def user_toggle(id):
    if not current_user.has_role("Super Admin"):
        abort(403)
    user = AdminUser.query.get_or_404(id)
    if user.id == current_user.id:
        flash("You cannot deactivate yourself.", "error")
        return redirect(url_for("admin.users"))
    user.is_active = not user.is_active
    db.session.commit()
    flash("User updated.", "success")
    return redirect(url_for("admin.users"))


# ── Testimonials ───────────────────────────────────────────────────────
@admin_bp.route("/testimonials", methods=["GET", "POST"])
@admin_required
def testimonials():
    from app.models import Testimonial
    if request.method == "POST":
        tm = Testimonial(
            client_name=request.form.get("client_name", "").strip(),
            company=request.form.get("company"),
            position_en=request.form.get("position_en"),
            position_ne=request.form.get("position_ne"),
            review_en=request.form.get("review_en"),
            review_ne=request.form.get("review_ne"),
            rating=int(request.form.get("rating") or 5),
            is_active=bool(request.form.get("is_active")),
            display_order=int(request.form.get("display_order") or 0),
        )
        db.session.add(tm)
        db.session.commit()
        flash("Testimonial added.", "success")
        return redirect(url_for("admin.testimonials"))
    items = Testimonial.query.order_by(Testimonial.display_order).all()
    return render_template("admin/testimonials.html", items=items)


@admin_bp.route("/testimonials/<int:id>/delete", methods=["POST"])
@admin_required
def testimonial_delete(id):
    from app.models import Testimonial
    tm = Testimonial.query.get_or_404(id)
    db.session.delete(tm)
    db.session.commit()
    flash("Deleted.", "success")
    return redirect(url_for("admin.testimonials"))


@admin_bp.route("/faqs", methods=["GET", "POST"])
@admin_required
def faqs():
    from app.models import FAQ
    if request.method == "POST":
        f = FAQ(
            question_en=request.form.get("question_en", "").strip(),
            question_ne=request.form.get("question_ne"),
            answer_en=request.form.get("answer_en"),
            answer_ne=request.form.get("answer_ne"),
            display_order=int(request.form.get("display_order") or 0),
            is_active=True,
        )
        db.session.add(f)
        db.session.commit()
        flash("FAQ added.", "success")
        return redirect(url_for("admin.faqs"))
    items = FAQ.query.order_by(FAQ.display_order).all()
    return render_template("admin/faqs.html", items=items)


@admin_bp.route("/faqs/<int:id>/delete", methods=["POST"])
@admin_required
def faq_delete(id):
    from app.models import FAQ
    f = FAQ.query.get_or_404(id)
    db.session.delete(f)
    db.session.commit()
    flash("Deleted.", "success")
    return redirect(url_for("admin.faqs"))


# ── Clients (logo wall) ────────────────────────────────────────────────
@admin_bp.route("/clients", methods=["GET", "POST"])
@admin_required
def clients():
    from app.models import Client
    from app.utils.media import upload_to_cloudinary

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            flash("Name is required.", "error")
            return redirect(url_for("admin.clients"))
        logo_url = None
        logo_public_id = None
        if "logo" in request.files and request.files["logo"].filename:
            result = upload_to_cloudinary(request.files["logo"], folder="bamstudio/clients")
            if result:
                logo_url = result.get("secure_url")
                logo_public_id = result.get("public_id")
        c = Client(
            name=name,
            logo_url=logo_url,
            logo_public_id=logo_public_id,
            website_url=request.form.get("website_url"),
            display_order=int(request.form.get("display_order") or 0),
            is_active=bool(request.form.get("is_active")),
        )
        db.session.add(c)
        db.session.commit()
        flash("Client added.", "success")
        return redirect(url_for("admin.clients"))
    items = Client.query.order_by(Client.display_order).all()
    return render_template("admin/clients.html", items=items)


@admin_bp.route("/clients/<int:id>/delete", methods=["POST"])
@admin_required
def client_delete(id):
    from app.models import Client
    c = Client.query.get_or_404(id)
    db.session.delete(c)
    db.session.commit()
    flash("Client deleted.", "success")
    return redirect(url_for("admin.clients"))


@admin_bp.route("/clients/<int:id>/edit", methods=["GET", "POST"])
@admin_required
def client_edit(id):
    from app.models import Client
    from app.utils.media import upload_to_cloudinary
    c = Client.query.get_or_404(id)
    if request.method == "POST":
        c.name = request.form.get("name", c.name).strip()
        c.website_url = request.form.get("website_url")
        c.display_order = int(request.form.get("display_order") or 0)
        c.is_active = bool(request.form.get("is_active"))
        if "logo" in request.files and request.files["logo"].filename:
            result = upload_to_cloudinary(request.files["logo"], folder="bamstudio/clients")
            if result:
                c.logo_url = result.get("secure_url") or result.get("url")
                c.logo_public_id = result.get("public_id")
        db.session.commit()
        flash("Client updated.", "success")
        return redirect(url_for("admin.clients"))
    return render_template("admin/client_edit.html", client=c)



# ── Team members ───────────────────────────────────────────────────────
@admin_bp.route("/team", methods=["GET", "POST"])
@admin_required
def team_members():
    from app.models import TeamMember
    from app.utils.media import upload_to_cloudinary

    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        if not name:
            flash("Name is required.", "error")
            return redirect(url_for("admin.team_members"))
        photo = None
        if "photo" in request.files and request.files["photo"].filename:
            result = upload_to_cloudinary(request.files["photo"], folder="bamstudio/team")
            if result:
                photo = result.get("secure_url") or result.get("url")
        skills_raw = request.form.get("skills") or ""
        skills = [s.strip() for s in skills_raw.split(",") if s.strip()]
        m = TeamMember(
            name=name,
            position_en=request.form.get("position_en"),
            position_ne=request.form.get("position_ne"),
            bio_en=request.form.get("bio_en"),
            bio_ne=request.form.get("bio_ne"),
            profile_image=photo,
            skills=skills or None,
            display_order=int(request.form.get("display_order") or 0),
            is_active=bool(request.form.get("is_active")),
        )
        db.session.add(m)
        db.session.flush()
        # Optional: create admin login for team member
        if request.form.get("create_login"):
            email = (request.form.get("login_email") or "").strip().lower()
            username = (request.form.get("login_username") or "").strip()
            password = request.form.get("login_password") or ""
            if email and username and password:
                if not AdminUser.query.filter(
                    (AdminUser.email == email) | (AdminUser.username == username)
                ).first():
                    role = Role.query.filter_by(name="Editor").first() or Role.query.first()
                    u = AdminUser(
                        email=email,
                        username=username,
                        full_name=name,
                        role_id=role.id if role else None,
                        is_active=True,
                    )
                    u.set_password(password)
                    db.session.add(u)
                    log_audit("created", "admin_user", None, username)
                    flash(f"Team member + login created ({username}).", "success")
                else:
                    flash("Team member added. Login email/username already exists.", "error")
            else:
                flash("Team member added. Login skipped (missing email/username/password).", "error")
        else:
            flash("Team member added.", "success")
        db.session.commit()
        try:
            log_audit("created", "team_member", m.id, m.name)
        except Exception:
            pass
        return redirect(url_for("admin.team_members"))
    items = TeamMember.query.order_by(TeamMember.display_order).all()
    return render_template("admin/team.html", items=items)


@admin_bp.route("/team/<int:id>/delete", methods=["POST"])
@admin_required
def team_delete(id):
    from app.models import TeamMember
    m = TeamMember.query.get_or_404(id)
    db.session.delete(m)
    db.session.commit()
    flash("Team member deleted.", "success")
    return redirect(url_for("admin.team_members"))


@admin_bp.route("/team/<int:id>/edit", methods=["GET", "POST"])
@admin_required
def team_edit(id):
    from app.models import TeamMember
    from app.utils.media import upload_to_cloudinary
    m = TeamMember.query.get_or_404(id)
    if request.method == "POST":
        m.name = (request.form.get("name") or m.name).strip()
        m.position_en = request.form.get("position_en")
        m.position_ne = request.form.get("position_ne")
        m.bio_en = request.form.get("bio_en")
        m.bio_ne = request.form.get("bio_ne")
        m.display_order = int(request.form.get("display_order") or 0)
        m.is_active = bool(request.form.get("is_active"))
        skills_raw = request.form.get("skills") or ""
        m.skills = [s.strip() for s in skills_raw.split(",") if s.strip()] or None
        if "photo" in request.files and request.files["photo"].filename:
            result = upload_to_cloudinary(request.files["photo"], folder="bamstudio/team")
            if result:
                m.profile_image = result.get("secure_url") or result.get("url")
        db.session.commit()
        flash("Team member updated.", "success")
        return redirect(url_for("admin.team_members"))
    return render_template("admin/team_edit.html", member=m)



@admin_bp.route("/media/<int:id>/edit", methods=["POST"])
@admin_required
def media_edit(id):
    item = Media.query.get_or_404(id)
    item.alt_text = request.form.get("alt_text") or item.alt_text
    item.original_filename = request.form.get("title") or item.original_filename
    db.session.commit()
    flash("Media details updated.", "success")
    return redirect(url_for("admin.media"))


@admin_bp.route("/media/<int:id>/delete", methods=["POST"])
@admin_required
def media_delete(id):
    item = Media.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash("Media deleted.", "success")
    return redirect(url_for("admin.media"))



@admin_bp.route("/stats", methods=["GET", "POST"])
@admin_required
def site_stats():
    from app.models import StatItem
    if request.method == "POST":
        item = StatItem(
            value=request.form.get("value", "").strip(),
            label_en=request.form.get("label_en", "").strip(),
            label_ne=request.form.get("label_ne"),
            display_order=int(request.form.get("display_order") or 0),
            is_active=bool(request.form.get("is_active")),
        )
        db.session.add(item)
        db.session.commit()
        flash("Stat added.", "success")
        return redirect(url_for("admin.site_stats"))
    items = StatItem.query.order_by(StatItem.display_order).all()
    return render_template("admin/stats.html", items=items)


@admin_bp.route("/stats/<int:id>/edit", methods=["POST"])
@admin_required
def stat_edit(id):
    from app.models import StatItem
    item = StatItem.query.get_or_404(id)
    item.value = request.form.get("value", item.value).strip()
    item.label_en = request.form.get("label_en", item.label_en).strip()
    item.label_ne = request.form.get("label_ne")
    item.display_order = int(request.form.get("display_order") or 0)
    item.is_active = bool(request.form.get("is_active"))
    db.session.commit()
    flash("Stat updated.", "success")
    return redirect(url_for("admin.site_stats"))


@admin_bp.route("/stats/<int:id>/delete", methods=["POST"])
@admin_required
def stat_delete(id):
    from app.models import StatItem
    item = StatItem.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    flash("Stat deleted.", "success")
    return redirect(url_for("admin.site_stats"))
