from datetime import date
from app.extensions import db
from app.models.application import JobApplication, ApplicationStatus
from app.models.status_history import StatusHistory

# Valid transitions — the state machine
VALID_TRANSITIONS = {
    ApplicationStatus.APPLIED: [ApplicationStatus.SCREENING, ApplicationStatus.REJECTED],
    ApplicationStatus.SCREENING: [ApplicationStatus.INTERVIEW, ApplicationStatus.REJECTED],
    ApplicationStatus.INTERVIEW: [ApplicationStatus.OFFER, ApplicationStatus.REJECTED],
    ApplicationStatus.OFFER: [ApplicationStatus.ACCEPTED, ApplicationStatus.REJECTED],
    ApplicationStatus.ACCEPTED: [],
    ApplicationStatus.REJECTED: [],
}


def create_application(user_id: int, data: dict) -> JobApplication:
    app = JobApplication(
        user_id=user_id,
        company=data["company"],
        role=data["role"],
        location=data.get("location"),
        applied_date=data["applied_date"],
        notes=data.get("notes"),
        source=data.get("source"),
        status=ApplicationStatus.APPLIED,
    )
    db.session.add(app)
    db.session.flush()  # get app.id before commit

    # Record initial status in history
    history = StatusHistory(
        application_id=app.id,
        from_status=None,
        to_status=ApplicationStatus.APPLIED,
    )
    db.session.add(history)
    db.session.commit()
    return app


def get_applications(user_id: int, status_filter: str = None) -> list:
    query = JobApplication.query.filter_by(user_id=user_id)
    if status_filter:
        try:
            status = ApplicationStatus(status_filter)
            query = query.filter_by(status=status)
        except ValueError:
            raise ValueError(f"Invalid status: {status_filter}")
    return query.order_by(JobApplication.applied_date.desc()).all()


def get_application(user_id: int, application_id: int) -> JobApplication:
    app = JobApplication.query.filter_by(id=application_id, user_id=user_id).first()
    if not app:
        raise LookupError("Application not found")
    return app


def update_application(user_id: int, application_id: int, data: dict) -> JobApplication:
    app = get_application(user_id, application_id)
    updatable = ["company", "role", "location", "notes", "source", "applied_date"]
    for field in updatable:
        if field in data:
            setattr(app, field, data[field])
    db.session.commit()
    return app


def transition_status(user_id: int, application_id: int, new_status_str: str) -> JobApplication:
    app = get_application(user_id, application_id)

    try:
        new_status = ApplicationStatus(new_status_str)
    except ValueError:
        raise ValueError(f"Invalid status: {new_status_str}")

    allowed = VALID_TRANSITIONS.get(app.status, [])
    if new_status not in allowed:
        raise ValueError(
            f"Cannot transition from '{app.status.value}' to '{new_status.value}'. "
            f"Allowed: {[s.value for s in allowed]}"
        )

    old_status = app.status
    app.status = new_status

    history = StatusHistory(
        application_id=app.id,
        from_status=old_status,
        to_status=new_status,
    )
    db.session.add(history)
    db.session.commit()
    return app


def delete_application(user_id: int, application_id: int) -> None:
    app = get_application(user_id, application_id)
    db.session.delete(app)
    db.session.commit()


def get_stats(user_id: int) -> dict:
    applications = JobApplication.query.filter_by(user_id=user_id).all()
    stats = {status.value: 0 for status in ApplicationStatus}
    for app in applications:
        stats[app.status.value] += 1
    return {"total": len(applications), "by_status": stats}