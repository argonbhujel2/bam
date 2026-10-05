from datetime import datetime
from app import db


class SiteSetting(db.Model):
    __tablename__ = "site_settings"

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False, index=True)
    value_en = db.Column(db.Text)
    value_ne = db.Column(db.Text)
    value_json = db.Column(db.JSON)
    group = db.Column(db.String(50), default="general")
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def get_value(self, lang="en"):
        if lang == "ne" and self.value_ne:
            return self.value_ne
        return self.value_en or ""

    def __repr__(self):
        return f"<SiteSetting {self.key}>"


class NavigationItem(db.Model):
    __tablename__ = "navigation_items"

    id = db.Column(db.Integer, primary_key=True)
    label_en = db.Column(db.String(100), nullable=False)
    label_ne = db.Column(db.String(100))
    url = db.Column(db.String(255), nullable=False)
    display_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    is_external = db.Column(db.Boolean, default=False)
    parent_id = db.Column(db.Integer, db.ForeignKey("navigation_items.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    children = db.relationship(
        "NavigationItem", backref=db.backref("parent", remote_side=[id]), lazy="dynamic"
    )

    def get_label(self, lang="en"):
        if lang == "ne" and self.label_ne:
            return self.label_ne
        return self.label_en

    def __repr__(self):
        return f"<NavigationItem {self.label_en}>"


class Page(db.Model):
    __tablename__ = "pages"

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(120), unique=True, nullable=False, index=True)
    title_en = db.Column(db.String(255), nullable=False)
    title_ne = db.Column(db.String(255))
    content_en = db.Column(db.Text)
    content_ne = db.Column(db.Text)
    meta_title_en = db.Column(db.String(255))
    meta_title_ne = db.Column(db.String(255))
    meta_description_en = db.Column(db.Text)
    meta_description_ne = db.Column(db.Text)
    og_image = db.Column(db.String(500))
    is_published = db.Column(db.Boolean, default=True)
    extra_data = db.Column(db.JSON)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def get_title(self, lang="en"):
        if lang == "ne" and self.title_ne:
            return self.title_ne
        return self.title_en

    def get_content(self, lang="en"):
        if lang == "ne" and self.content_ne:
            return self.content_ne
        return self.content_en or ""

    def get_meta_title(self, lang="en"):
        if lang == "ne" and self.meta_title_ne:
            return self.meta_title_ne
        return self.meta_title_en or self.get_title(lang)

    def get_meta_description(self, lang="en"):
        if lang == "ne" and self.meta_description_ne:
            return self.meta_description_ne
        return self.meta_description_en or ""

    def __repr__(self):
        return f"<Page {self.slug}>"


class Service(db.Model):
    __tablename__ = "services"

    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(10), default="01")
    title_en = db.Column(db.String(150), nullable=False)
    title_ne = db.Column(db.String(150))
    description_en = db.Column(db.Text)
    description_ne = db.Column(db.Text)
    detail_en = db.Column(db.Text)
    detail_ne = db.Column(db.Text)
    icon = db.Column(db.String(255))
    image = db.Column(db.String(500))
    is_active = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)
    display_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def get_title(self, lang="en"):
        if lang == "ne" and self.title_ne:
            return self.title_ne
        return self.title_en

    def get_description(self, lang="en"):
        if lang == "ne" and self.description_ne:
            return self.description_ne
        return self.description_en or ""

    def get_detail(self, lang="en"):
        if lang == "ne" and self.detail_ne:
            return self.detail_ne
        return self.detail_en or ""

    def __repr__(self):
        return f"<Service {self.title_en}>"


class ProcessStep(db.Model):
    __tablename__ = "process_steps"

    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.String(10), default="01")
    title_en = db.Column(db.String(100), nullable=False)
    title_ne = db.Column(db.String(100))
    description_en = db.Column(db.Text)
    description_ne = db.Column(db.Text)
    display_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_title(self, lang="en"):
        if lang == "ne" and self.title_ne:
            return self.title_ne
        return self.title_en

    def get_description(self, lang="en"):
        if lang == "ne" and self.description_ne:
            return self.description_ne
        return self.description_en or ""

    def __repr__(self):
        return f"<ProcessStep {self.title_en}>"


class TeamMember(db.Model):
    __tablename__ = "team_members"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    position_en = db.Column(db.String(120))
    position_ne = db.Column(db.String(120))
    bio_en = db.Column(db.Text)
    bio_ne = db.Column(db.Text)
    profile_image = db.Column(db.String(500))
    skills = db.Column(db.JSON)
    social_links = db.Column(db.JSON)
    display_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_position(self, lang="en"):
        if lang == "ne" and self.position_ne:
            return self.position_ne
        return self.position_en or ""

    def get_bio(self, lang="en"):
        if lang == "ne" and self.bio_ne:
            return self.bio_ne
        return self.bio_en or ""

    def __repr__(self):
        return f"<TeamMember {self.name}>"



class Testimonial(db.Model):
    __tablename__ = "testimonials"

    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(120), nullable=False)
    company = db.Column(db.String(150))
    position_en = db.Column(db.String(120))
    position_ne = db.Column(db.String(120))
    photo = db.Column(db.String(500))
    review_en = db.Column(db.Text)
    review_ne = db.Column(db.Text)
    rating = db.Column(db.Integer, default=5)
    is_active = db.Column(db.Boolean, default=True)
    display_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_position(self, lang="en"):
        if lang == "ne" and self.position_ne:
            return self.position_ne
        return self.position_en or ""

    def get_review(self, lang="en"):
        if lang == "ne" and self.review_ne:
            return self.review_ne
        return self.review_en or ""

    def __repr__(self):
        return f"<Testimonial {self.client_name}>"


class FAQ(db.Model):
    __tablename__ = "faqs"

    id = db.Column(db.Integer, primary_key=True)
    question_en = db.Column(db.String(500), nullable=False)
    question_ne = db.Column(db.String(500))
    answer_en = db.Column(db.Text)
    answer_ne = db.Column(db.Text)
    display_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_question(self, lang="en"):
        if lang == "ne" and self.question_ne:
            return self.question_ne
        return self.question_en

    def get_answer(self, lang="en"):
        if lang == "ne" and self.answer_ne:
            return self.answer_ne
        return self.answer_en or ""

    def __repr__(self):
        return f"<FAQ {self.question_en[:40]}>"


class TechItem(db.Model):
    __tablename__ = "tech_items"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    category = db.Column(db.String(80), default="general")  # language, framework, db, tool
    display_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f"<TechItem {self.name}>"


class StatItem(db.Model):
    __tablename__ = "stat_items"

    id = db.Column(db.Integer, primary_key=True)
    label_en = db.Column(db.String(120), nullable=False)
    label_ne = db.Column(db.String(120))
    value = db.Column(db.String(40), nullable=False)  # e.g. "7+", "Nepal"
    display_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)

    def get_label(self, lang="en"):
        if lang == "ne" and self.label_ne:
            return self.label_ne
        return self.label_en

    def __repr__(self):
        return f"<StatItem {self.value} {self.label_en}>"



class Client(db.Model):
    __tablename__ = "clients"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    logo_url = db.Column(db.String(500))
    logo_public_id = db.Column(db.String(255))
    website_url = db.Column(db.String(500))
    display_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Client {self.name}>"
