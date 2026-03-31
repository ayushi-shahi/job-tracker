import enum
from datetime import datetime, timezone
from app.extensions import db


class ApplicationStatus(enum.Enum):
    APPLIED = "applied"
    SCREENING = "screening"
    INTERVIEW = "interview"
    OFFER = "offer"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class JobApplication(db.Model):
    __tablename__ = "job_applications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    company = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(255))
    status = db.Column(db.Enum(ApplicationStatus), nullable=False, default=ApplicationStatus.APPLIED)
    applied_date = db.Column(db.Date, nullable=False)
    notes = db.Column(db.Text)
    source = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    user = db.relationship("User", back_populates="applications")
    status_history = db.relationship(
        "StatusHistory",
        back_populates="application",
        order_by="StatusHistory.changed_at",
        cascade="all, delete-orphan",
    )