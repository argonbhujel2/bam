from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    g,
    make_response,
    current_app,
)
from app import db, limiter
from app.models import (
    Project,
    ProjectCategory,
    Service,
    ProcessStep,
    Career,
    CareerApplication,
    ContactInquiry,
    ProjectInquiry,
    TeamMember,
    Page,
    Testimonial,
    FAQ,
    TechItem,
    StatItem,
    Client,
    Media,
)
from app.utils.helpers import get_setting, t
from app.utils.media import upload_to_cloudinary, save_media_record, allowed_file
from app.utils.email import notify_project_inquiry, notify_contact_message, notify_career_application
from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    TextAreaField,
    SelectField,
    EmailField,
    TelField,
    FileField,
    SubmitField,
)
from wtforms.validators import DataRequired, Email, Optional, Length
from datetime import datetime

public_bp = Blueprint("public", __name__)


# ── Forms ──────────────────────────────────────────────────────────────
class ContactForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=150)])
    email = EmailField("Email", validators=[DataRequired(), Email()])
    phone = TelField("Phone", validators=[Optional(), Length(max=50)])
    subject = StringField("Subject", validators=[Optional(), Length(max=255)])
    message = TextAreaField("Message", validators=[DataRequired(), Length(max=5000)])
    submit = SubmitField("Send Message")


class ProjectInquiryForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=150)])
    email = EmailField("Email", validators=[DataRequired(), Email()])
    phone = TelField("Phone", validators=[Optional(), Length(max=50)])
    company = StringField("Company", validators=[Optional(), Length(max=150)])
    project_type = SelectField(
        "Project Type",
        choices=[
            ("Website", "Website"),
            ("E-commerce", "E-commerce"),
            ("Custom Software", "Custom Software"),
            ("Business Management System", "Business Management System"),
            ("UI/UX", "UI/UX"),
            ("Automation", "Automation"),
            ("Other", "Other"),
        ],
        validators=[DataRequired()],
    )
    budget = SelectField(
        "Budget",
        choices=[
            ("", "Select budget range"),
            ("Under $1,000", "Under $1,000"),
            ("$1,000 – $5,000", "$1,000 – $5,000"),
            ("$5,000 – $15,000", "$5,000 – $15,000"),
            ("$15,000+", "$15,000+"),
            ("To be discussed", "To be discussed"),
        ],
        validators=[Optional()],
    )
    message = TextAreaField("Message", validators=[DataRequired(), Length(max=5000)])
    submit = SubmitField("Send Inquiry")


class CareerApplicationForm(FlaskForm):
    full_name = StringField("Full Name", validators=[DataRequired(), Length(max=150)])
    email = EmailField("Email", validators=[DataRequired(), Email()])
    phone = TelField("Phone", validators=[Optional(), Length(max=50)])
    experience = StringField("Experience", validators=[Optional(), Length(max=100)])
    portfolio = StringField("Portfolio URL", validators=[Optional(), Length(max=500)])
    github = StringField("GitHub URL", validators=[Optional(), Length(max=500)])
    linkedin = StringField("LinkedIn URL", validators=[Optional(), Length(max=500)])
    cv = FileField("CV / Resume")
    cover_message = TextAreaField("Cover Message", validators=[Optional(), Length(max=5000)])
    submit = SubmitField("Submit Application")


# ── Language switcher ──────────────────────────────────────────────────
@public_bp.route("/set-language/<lang>")
def set_language(lang):
    if lang not in ("en", "ne"):
        lang = "en"
    resp = make_response(redirect(request.referrer or url_for("public.home")))
    resp.set_cookie("lang", lang, max_age=60 * 60 * 24 * 365)
    return resp


# ── Home ───────────────────────────────────────────────────────────────
@public_bp.route("/")
def home():
    lang = g.lang
    services = (
        Service.query.filter_by(is_active=True)
        .order_by(Service.display_order)
        .limit(6)
        .all()
    )
    projects = (
        Project.query.filter_by(is_published=True, is_featured=True)
        .order_by(Project.display_order)
        .limit(6)
        .all()
    )
    process_steps = (
        ProcessStep.query.filter_by(is_active=True)
        .order_by(ProcessStep.display_order)
        .all()
    )
    open_careers_count = Career.query.filter_by(status="open").count()
    testimonials = (
        Testimonial.query.filter_by(is_active=True)
        .order_by(Testimonial.display_order)
        .all()
    )
    faqs = FAQ.query.filter_by(is_active=True).order_by(FAQ.display_order).all()
    tech_items = TechItem.query.filter_by(is_active=True).order_by(TechItem.display_order).all()
    stats = StatItem.query.filter_by(is_active=True).order_by(StatItem.display_order).all()
    clients = Client.query.filter_by(is_active=True).order_by(Client.display_order).all()
    _media_all = Media.query.order_by(Media.created_at.desc()).limit(60).all()
    media_items = []
    for m in _media_all:
        u = (m.url or "").lower()
        fmt = (m.format or "").lower()
        if any(u.endswith(e) or fmt == e.strip(".") for e in (".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg", "png", "jpg", "jpeg", "webp", "gif", "svg")):
            media_items.append(m)
        if len(media_items) >= 24:
            break
    client_names = [c.name for c in clients]
    if not clients:
        # Fallback text wall from project.client names
        _seen = set()
        for pr in Project.query.filter_by(is_published=True).order_by(Project.display_order).all():
            if pr.client and pr.client not in _seen:
                _seen.add(pr.client)
                client_names.append(pr.client)

    hero = {
        "heading_en": get_setting("hero_heading", "WE BUILD DIGITAL EXPERIENCES."),
        "heading_ne": get_setting("hero_heading", "हामी डिजिटल अनुभव निर्माण गर्छौं।", lang="ne") if False else get_setting("hero_heading", "हामी डिजिटल अनुभव निर्माण गर्छौं।"),
        "desc_en": get_setting("hero_desc", "Websites, systems and digital solutions engineered for modern businesses."),
        "desc_ne": get_setting("hero_desc", "आधुनिक व्यवसायका लागि वेबसाइट, प्रणाली तथा डिजिटल समाधान निर्माण गर्छौं।"),
    }
    # bilingual hero via settings get_value
    from app.models import SiteSetting
    hh = SiteSetting.query.filter_by(key="hero_heading").first()
    hd = SiteSetting.query.filter_by(key="hero_desc").first()
    if hh:
        hero["heading_en"] = hh.value_en or hero["heading_en"]
        hero["heading_ne"] = hh.value_ne or hero["heading_ne"]
    if hd:
        hero["desc_en"] = hd.value_en or hero["desc_en"]
        hero["desc_ne"] = hd.value_ne or hero["desc_ne"]

    return render_template(
        "public/home.html",
        services=services,
        projects=projects,
        process_steps=process_steps,
        open_careers_count=open_careers_count,
        hero=hero,
        testimonials=testimonials,
        faqs=faqs,
        tech_items=tech_items,
        client_names=client_names,
        clients=clients,
        media_items=media_items,
        stats=stats,
    )




@public_bp.route("/behind-the-work")
def behind_the_work():
    """Gallery of Media Library images — Behind the work."""
    _media_all = Media.query.order_by(Media.created_at.desc()).limit(60).all()
    media_items = []
    for m in _media_all:
        u = (m.url or "").lower()
        fmt = (m.format or "").lower()
        if any(
            u.endswith(e) or fmt == e.strip(".")
            for e in (".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg", "png", "jpg", "jpeg", "webp", "gif", "svg")
        ):
            media_items.append(m)
    return render_template("public/behind_the_work.html", media_items=media_items)

# ── About ──────────────────────────────────────────────────────────────
@public_bp.route("/about")
def about():
    team = (
        TeamMember.query.filter_by(is_active=True)
        .order_by(TeamMember.display_order)
        .all()
    )
    process_steps = (
        ProcessStep.query.filter_by(is_active=True)
        .order_by(ProcessStep.display_order)
        .all()
    )
    return render_template("public/about.html", team=team, process_steps=process_steps)


@public_bp.route("/founder")
def founder():
    projects = (
        Project.query.filter_by(is_published=True)
        .order_by(Project.display_order)
        .limit(8)
        .all()
    )
    tech_items = TechItem.query.filter_by(is_active=True).order_by(TechItem.display_order).all()
    return render_template("public/founder.html", projects=projects, tech_items=tech_items)


# ── Services ───────────────────────────────────────────────────────────
@public_bp.route("/services")
def services():
    services_list = (
        Service.query.filter_by(is_active=True)
        .order_by(Service.display_order)
        .all()
    )
    stats = StatItem.query.filter_by(is_active=True).order_by(StatItem.display_order).all()
    return render_template("public/services.html", services=services_list, stats=stats)


@public_bp.route("/services/<int:id>")
def service_detail(id):
    s = Service.query.filter_by(id=id, is_active=True).first_or_404()
    others = (
        Service.query.filter(Service.is_active == True, Service.id != s.id)
        .order_by(Service.display_order)
        .limit(4)
        .all()
    )
    return render_template("public/service_detail.html", service=s, others=others)


# ── Work / Portfolio ───────────────────────────────────────────────────
@public_bp.route("/work")
def work():
    category_slug = request.args.get("category")
    categories = (
        ProjectCategory.query.filter_by(is_active=True)
        .order_by(ProjectCategory.display_order)
        .all()
    )
    query = Project.query.filter_by(is_published=True)
    if category_slug and category_slug != "all":
        cat = ProjectCategory.query.filter_by(slug=category_slug).first()
        if cat:
            query = query.filter_by(category_id=cat.id)
    projects = query.order_by(Project.display_order, Project.created_at.desc()).all()
    return render_template(
        "public/work.html",
        projects=projects,
        categories=categories,
        active_category=category_slug or "all",
    )


@public_bp.route("/work/<slug>")
def project_detail(slug):
    project = Project.query.filter_by(slug=slug, is_published=True).first_or_404()
    related = (
        Project.query.filter(
            Project.is_published == True,
            Project.id != project.id,
            Project.category_id == project.category_id,
        )
        .limit(3)
        .all()
    )
    return render_template(
        "public/project_detail.html", project=project, related=related
    )


# ── Careers ────────────────────────────────────────────────────────────
@public_bp.route("/careers")
def careers():
    vacancies = (
        Career.query.filter_by(status="open")
        .order_by(Career.display_order, Career.created_at.desc())
        .all()
    )
    return render_template("public/careers.html", vacancies=vacancies)


@public_bp.route("/careers/<slug>", methods=["GET", "POST"])
@limiter.limit("10 per hour")
def career_detail(slug):
    career = Career.query.filter_by(slug=slug, status="open").first_or_404()
    form = CareerApplicationForm()
    if form.validate_on_submit():
        cv_url = None
        cv_public_id = None
        if form.cv.data and form.cv.data.filename:
            if not allowed_file(
                form.cv.data.filename,
                current_app.config.get("ALLOWED_CV_EXTENSIONS"),
            ):
                flash(
                    t(
                        "Invalid file type. Please upload PDF or Word document.",
                        "अमान्य फाइल प्रकार। कृपया PDF वा Word दस्तावेज अपलोड गर्नुहोस्।",
                    ),
                    "error",
                )
                return render_template(
                    "public/career_detail.html", career=career, form=form
                )
            result = upload_to_cloudinary(
                form.cv.data, folder="bamstudio/cvs", resource_type="raw"
            )
            if result:
                cv_url = result.get("secure_url")
                cv_public_id = result.get("public_id")

        app = CareerApplication(
            career_id=career.id,
            full_name=form.full_name.data.strip(),
            email=form.email.data.strip().lower(),
            phone=form.phone.data,
            experience=form.experience.data,
            portfolio_url=form.portfolio.data,
            github_url=form.github.data,
            linkedin_url=form.linkedin.data,
            cv_url=cv_url,
            cv_public_id=cv_public_id,
            cover_message=form.cover_message.data,
        )
        db.session.add(app)
        db.session.commit()
        try:
            notify_career_application(app)
        except Exception:
            pass
        flash(
            t(
                "Thank you for applying. Our team will review your application.",
                "आवेदन दिनुभएकोमा धन्यवाद। हाम्रो टोलीले तपाईंको आवेदन समीक्षा गर्नेछ।",
            ),
            "success",
        )
        return redirect(url_for("public.careers"))
    return render_template("public/career_detail.html", career=career, form=form)


# ── Contact ────────────────────────────────────────────────────────────
@public_bp.route("/contact", methods=["GET", "POST"])
@limiter.limit("15 per hour")
def contact():
    form = ContactForm()
    inquiry_form = ProjectInquiryForm()
    # Prefer form_type so the correct form is validated
    if request.method == "POST" and request.form.get("form_type") == "contact" and form.validate_on_submit():
        inquiry = ContactInquiry(
            name=form.name.data.strip(),
            email=form.email.data.strip().lower(),
            phone=form.phone.data,
            subject=form.subject.data,
            message=form.message.data.strip(),
            ip_address=request.remote_addr,
        )
        db.session.add(inquiry)
        db.session.commit()
        try:
            notify_contact_message(inquiry)
        except Exception:
            pass
        flash(
            t(
                "Thank you. We have received your message and will get back to you soon.",
                "धन्यवाद। हामीले तपाईंको सन्देश प्राप्त गर्यौं र चाँडै सम्पर्क गर्नेछौं।",
            ),
            "success",
        )
        return redirect(url_for("public.contact"))

    if request.method == "POST" and request.form.get("form_type") == "inquiry" and inquiry_form.validate_on_submit():
        inq = ProjectInquiry(
            name=inquiry_form.name.data.strip(),
            email=inquiry_form.email.data.strip().lower(),
            phone=inquiry_form.phone.data,
            company=inquiry_form.company.data,
            project_type=inquiry_form.project_type.data,
            budget=inquiry_form.budget.data,
            message=inquiry_form.message.data.strip(),
            ip_address=request.remote_addr,
        )
        db.session.add(inq)
        db.session.commit()
        try:
            notify_project_inquiry(inq)
        except Exception:
            pass
        flash(
            t(
                "Thank you for your project inquiry. We will review it and contact you shortly.",
                "तपाईंको परियोजना सोधपुछको लागि धन्यवाद। हामी समीक्षा गरेर चाँडै सम्पर्क गर्नेछौं।",
            ),
            "success",
        )
        return redirect(url_for("public.contact"))

    return render_template(
        "public/contact.html", form=form, inquiry_form=inquiry_form
    )


# ── SEO ────────────────────────────────────────────────────────────────
@public_bp.route("/robots.txt")
def robots():
    site_url = current_app.config.get("SITE_URL", "")
    content = f"""User-agent: *
Allow: /
Disallow: /admin/
Disallow: /api/
Sitemap: {site_url}/sitemap.xml
"""
    resp = make_response(content)
    resp.headers["Content-Type"] = "text/plain"
    return resp


@public_bp.route("/sitemap.xml")
def sitemap():
    pages = [
        {"loc": "/", "priority": "1.0"},
        {"loc": "/about", "priority": "0.8"},
        {"loc": "/services", "priority": "0.8"},
        {"loc": "/work", "priority": "0.9"},
        {"loc": "/careers", "priority": "0.7"},
        {"loc": "/contact", "priority": "0.8"},
    ]
    projects = Project.query.filter_by(is_published=True).all()
    for p in projects:
        pages.append({"loc": f"/work/{p.slug}", "priority": "0.7"})
    careers = Career.query.filter_by(status="open").all()
    for c in careers:
        pages.append({"loc": f"/careers/{c.slug}", "priority": "0.6"})

    site_url = current_app.config.get("SITE_URL", "")
    xml = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    for p in pages:
        xml.append("<url>")
        xml.append(f"<loc>{site_url}{p['loc']}</loc>")
        xml.append(f"<priority>{p['priority']}</priority>")
        xml.append("</url>")
    xml.append("</urlset>")
    resp = make_response("\n".join(xml))
    resp.headers["Content-Type"] = "application/xml"
    return resp
