from datetime import datetime
from slugify import slugify
from app import db


class ProjectCategory(db.Model):
    __tablename__ = "project_categories"

    id = db.Column(db.Integer, primary_key=True)
    name_en = db.Column(db.String(80), nullable=False, unique=True)
    name_ne = db.Column(db.String(80))
    slug = db.Column(db.String(80), unique=True, nullable=False)
    display_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)

    projects = db.relationship("Project", back_populates="category", lazy="dynamic")

    def get_name(self, lang="en"):
        if lang == "ne" and self.name_ne:
            return self.name_ne
        return self.name_en

    def __repr__(self):
        return f"<ProjectCategory {self.name_en}>"


class Project(db.Model):
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    slug = db.Column(db.String(200), unique=True, nullable=False, index=True)
    description_en = db.Column(db.Text)
    description_ne = db.Column(db.Text)
    full_description_en = db.Column(db.Text)
    full_description_ne = db.Column(db.Text)
    challenge_en = db.Column(db.Text)
    challenge_ne = db.Column(db.Text)
    solution_en = db.Column(db.Text)
    solution_ne = db.Column(db.Text)
    features_en = db.Column(db.Text)
    features_ne = db.Column(db.Text)
    client = db.Column(db.String(150))
    location = db.Column(db.String(150))
    technologies = db.Column(db.JSON)  # list of strings
    cover_image = db.Column(db.String(500))
    video_url = db.Column(db.String(500))
    live_url = db.Column(db.String(500))
    github_url = db.Column(db.String(500))
    project_year = db.Column(db.String(10))
    status = db.Column(db.String(40), default="Completed")  # Completed, In Progress, Live
    result_en = db.Column(db.Text)
    result_ne = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey("project_categories.id"))
    category = db.relationship("ProjectCategory", back_populates="projects")
    is_featured = db.Column(db.Boolean, default=False)
    is_published = db.Column(db.Boolean, default=False)
    display_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    images = db.relationship(
        "ProjectImage",
        back_populates="project",
        cascade="all, delete-orphan",
        order_by="ProjectImage.display_order",
    )

    def get_description(self, lang="en"):
        if lang == "ne" and self.description_ne:
            return self.description_ne
        return self.description_en or ""

    def get_full_description(self, lang="en"):
        if lang == "ne" and self.full_description_ne:
            return self.full_description_ne
        return self.full_description_en or ""

    def get_challenge(self, lang="en"):
        if lang == "ne" and self.challenge_ne:
            return self.challenge_ne
        return self.challenge_en or ""

    def get_solution(self, lang="en"):
        if lang == "ne" and self.solution_ne:
            return self.solution_ne
        return self.solution_en or ""

    def get_features(self, lang="en"):
        if lang == "ne" and self.features_ne:
            return self.features_ne
        return self.features_en or ""

    def get_result(self, lang="en"):
        if lang == "ne" and self.result_ne:
            return self.result_ne
        return self.result_en or ""

    @staticmethod
    def generate_slug(title):
        return slugify(title)

    def __repr__(self):
        return f"<Project {self.title}>"


class ProjectImage(db.Model):
    __tablename__ = "project_images"

    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey("projects.id"), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    public_id = db.Column(db.String(255))
    alt_text = db.Column(db.String(255))
    display_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    project = db.relationship("Project", back_populates="images")

    def __repr__(self):
        return f"<ProjectImage {self.id}>"
