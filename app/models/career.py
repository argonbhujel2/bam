from datetime import datetime
from slugify import slugify
from app import db


class Career(db.Model):
    __tablename__ = "careers"

    id = db.Column(db.Integer, primary_key=True)
    title_en = db.Column(db.String(150), nullable=False)
    title_ne = db.Column(db.String(150))
    slug = db.Column(db.String(150), unique=True, nullable=False, index=True)
    department = db.Column(db.String(100))
    location = db.Column(db.String(150), default="Remote / Nepal")
    employment_type = db.Column(db.String(50), default="Full-time")  # Full-time, Part-time, Contract, Intern
    experience = db.Column(db.String(100))
    salary_range = db.Column(db.String(100))
    description_en = db.Column(db.Text)
    description_ne = db.Column(db.Text)
    responsibilities_en = db.Column(db.Text)
    responsibilities_ne = db.Column(db.Text)
    requirements_en = db.Column(db.Text)
    requirements_ne = db.Column(db.Text)
    skills = db.Column(db.JSON)  # list
    deadline = db.Column(db.Date)
    status = db.Column(db.String(20), default="draft")  # draft, open, closed
    display_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    applications = db.relationship(
        "CareerApplication", back_populates="career", cascade="all, delete-orphan"
    )

    def get_title(self, lang="en"):
        if lang == "ne" and self.title_ne:
            return self.title_ne
        return self.title_en

    def get_description(self, lang="en"):
        if lang == "ne" and self.description_ne:
            return self.description_ne
        return self.description_en or ""

    def get_responsibilities(self, lang="en"):
        if lang == "ne" and self.responsibilities_ne:
            return self.responsibilities_ne
        return self.responsibilities_en or ""

    def get_requirements(self, lang="en"):
        if lang == "ne" and self.requirements_ne:
            return self.requirements_ne
        return self.requirements_en or ""

    @property
    def is_open(self):
        return self.status == "open"

    @staticmethod
    def generate_slug(title):
        return slugify(title)

    def __repr__(self):
        return f"<Career {self.title_en}>"


class CareerApplication(db.Model):
    __tablename__ = "career_applications"

    id = db.Column(db.Integer, primary_key=True)
    career_id = db.Column(db.Integer, db.ForeignKey("careers.id"), nullable=False)
    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(255), nullable=False, index=True)
    phone = db.Column(db.String(50))
    experience = db.Column(db.String(100))
    portfolio_url = db.Column(db.String(500))
    github_url = db.Column(db.String(500))
    linkedin_url = db.Column(db.String(500))
    cv_url = db.Column(db.String(500))  # Cloudinary or secure storage URL
    cv_public_id = db.Column(db.String(255))
    cover_message = db.Column(db.Text)
    status = db.Column(
        db.String(30), default="new"
    )  # new, shortlisted, interview, selected, rejected
    internal_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    career = db.relationship("Career", back_populates="applications")

    def __repr__(self):
        return f"<CareerApplication {self.full_name}>"
