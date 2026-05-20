from datetime import datetime, timezone

from app.extensions import db


class Report(db.Model):
    __tablename__ = "reports"

    id = db.Column(db.Integer, primary_key=True)
    source_id = db.Column(db.String(32), db.ForeignKey("water_sources.id"), nullable=False)
    reporter_phone_hash = db.Column(db.String(64))
    cause_category = db.Column(db.String(64), nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    channel = db.Column(db.String(16), default="web")

    source = db.relationship("WaterSource", back_populates="reports")
    repair_case = db.relationship("RepairCase", back_populates="report", uselist=False)
