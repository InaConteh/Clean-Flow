"""Seed sample water sources for development."""

from datetime import datetime, timezone

from app import create_app
from app.extensions import db
from app.models.water_source import WaterSource, WaterSourceStatus


SAMPLE_SOURCES = [
    {
        "id": "WELL123",
        "name": "Bo Community Well",
        "latitude": 8.4844,
        "longitude": -13.2344,
        "status": WaterSourceStatus.SAFE,
        "district": "Western Area",
    },
    {
        "id": "WELL456",
        "name": "Kenema Borehole",
        "latitude": 7.8763,
        "longitude": -11.1903,
        "status": WaterSourceStatus.CAUTION,
        "district": "Kenema",
    },
    {
        "id": "WELL789",
        "name": "Makeni Pump Station",
        "latitude": 8.8864,
        "longitude": -12.0442,
        "status": WaterSourceStatus.SAFE,
        "district": "Bombali",
    },
]


def seed():
    app = create_app()
    with app.app_context():
        db.create_all()
        for data in SAMPLE_SOURCES:
            if not WaterSource.query.get(data["id"]):
                db.session.add(
                    WaterSource(
                        **data,
                        last_tested=datetime.now(timezone.utc),
                    )
                )
        db.session.commit()
        print(f"Seeded {len(SAMPLE_SOURCES)} water sources.")


if __name__ == "__main__":
    seed()
