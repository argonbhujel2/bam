from datetime import datetime
from app import db


class ContactInquiry(db.Model):
    __tablename__ = "contact_inquiries"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(255), nullable=False, index=True)
    phone = db.Column(db.String(50))
    subject = db.Column(db.String(255))
    message = db.Column(db.Text, nullable=False)
    status = db.Column(
        db.String(30), default="new"
    )  # new, contacted, in_discussion, converted, closed
    internal_notes = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self):
        return f"<ContactInquiry {self.email}>"


class ProjectInquiry(db.Model):
    __tablename__ = "project_inquiries"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(255), nullable=False, index=True)
    phone = db.Column(db.String(50))
    company = db.Column(db.String(150))
    project_type = db.Column(db.String(100))  # Website, E-commerce, Custom Software, etc.
    budget = db.Column(db.String(100))
    message = db.Column(db.Text, nullable=False)
    status = db.Column(
        db.String(30), default="new"
    )  # new, contacted, in_discussion, converted, closed
    internal_notes = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def __repr__(self):
        return f"<ProjectInquiry {self.email}>"
