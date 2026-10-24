from datetime import datetime
from app import db


class Media(db.Model):
    __tablename__ = "media"

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255))
    url = db.Column(db.String(500), nullable=False)
    public_id = db.Column(db.String(255))  # Cloudinary public_id
    resource_type = db.Column(db.String(50), default="image")  # image, video, raw
    format = db.Column(db.String(20))
    mime_type = db.Column(db.String(100))
    size_bytes = db.Column(db.Integer)
    width = db.Column(db.Integer)
    height = db.Column(db.Integer)
    alt_text = db.Column(db.String(255))
    folder = db.Column(db.String(100), default="bamstudio")
    uploaded_by = db.Column(db.Integer, db.ForeignKey("admin_users.id"))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    uploader = db.relationship("AdminUser", backref="uploads")

    def __repr__(self):
        return f"<Media {self.filename}>"
