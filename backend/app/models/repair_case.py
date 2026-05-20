from datetime import datetime, timezone

from app.extensions import db


class RepairStatus:
    REPORTED = "reported"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"


class RepairCase(db.Model):
    __tablename__ = "repair_cases"

    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey("reports.id"), nullable=False, unique=True)
    assigned_team = db.Column(db.String(128))
    eta = db.Column(db.DateTime)
    status = db.Column(db.String(32), default=RepairStatus.REPORTED)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    resolved_at = db.Column(db.DateTime)

    report = db.relationship("Report", back_populates="repair_case")
