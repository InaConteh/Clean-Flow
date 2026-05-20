from datetime import datetime, timezone

from app.extensions import db


class WaterSourceStatus:
    SAFE = "green"
    CAUTION = "yellow"
    UNSAFE = "red"


class WaterSource(db.Model):
    __tablename__ = "water_sources"

    id = db.Column(db.String(32), primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(16), nullable=False, default=WaterSourceStatus.SAFE)
    last_tested = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    district = db.Column(db.String(128))
    committee_phone = db.Column(db.String(32))
    preferred_language = db.Column(db.String(10), default="en")
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    reports = db.relationship("Report", back_populates="source", lazy="dynamic")
    maintenance_logs = db.relationship("MaintenanceLog", back_populates="source", lazy="dynamic")

    def to_geojson_feature(self):
        return {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [self.longitude, self.latitude],
            },
            "properties": {
                "id": self.id,
                "name": self.name,
                "status": self.status,
                "last_tested": self.last_tested.isoformat() if self.last_tested else None,
                "district": self.district,
            },
        }
