from datetime import datetime
from app import db


class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)
    admin_user_id = db.Column(db.Integer, db.ForeignKey("admin_users.id"))
    action = db.Column(db.String(100), nullable=False)  # created, updated, deleted, published, etc.
    module = db.Column(db.String(80), nullable=False)  # project, career, service, etc.
    record_id = db.Column(db.Integer)
    record_title = db.Column(db.String(255))
    details = db.Column(db.Text)
    ip_address = db.Column(db.String(45))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    admin_user = db.relationship("AdminUser", backref="audit_logs")

    def __repr__(self):
        return f"<AuditLog {self.action} {self.module}>"
