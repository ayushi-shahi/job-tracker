from datetime import datetime, timezone
from app.extensions import db
from app.models.application import ApplicationStatus


class StatusHistory(db.Model):
    __tablename__ = "status_history"

    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey("job_applications.id"), nullable=False)
    from_status = db.Column(db.Enum(ApplicationStatus), nullable=True)  # None on creation
    to_status = db.Column(db.Enum(ApplicationStatus), nullable=False)
    changed_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    application = db.relationship("JobApplication", back_populates="status_history")