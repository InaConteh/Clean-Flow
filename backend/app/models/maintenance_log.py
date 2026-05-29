from datetime import datetime, timezone

from app.extensions import db


class MaintenanceLog(db.Model):
    __tablename__ = "maintenance_logs"

    id = db.Column(db.Integer, primary_key=True)
    source_id = db.Column(db.String(32), db.ForeignKey("water_sources.id"), nullable=False)
    task_type = db.Column(db.String(64), nullable=False)
    scheduled_date = db.Column(db.DateTime)
    completion_status = db.Column(db.String(32), default="pending")
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    source = db.relationship("WaterSource", back_populates="maintenance_logs")
