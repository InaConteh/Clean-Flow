import pytest
import json
from app import create_app
from app.extensions import db
from app.models.water_source import WaterSource, WaterSourceStatus
from app.models.report import Report
from app.models.repair_case import RepairCase, RepairStatus
from app.models.user import User, UserRole
from datetime import datetime, timedelta, timezone

@pytest.fixture
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        official = User(username="official", role=UserRole.DISTRICT_OFFICIAL)
        official.set_password("pass")
        source = WaterSource(id="WELL1", name="Well 1", district="Bo", latitude=0.0, longitude=0.0, status=WaterSourceStatus.SAFE)
        db.session.add_all([official, source])
        db.session.commit()

        # Create a resolved case for analytics
        report = Report(source_id="WELL1", cause_category="PUMP", timestamp=datetime.now(timezone.utc) - timedelta(hours=10))
        db.session.add(report)
        db.session.flush()
        case = RepairCase(report_id=report.id, status=RepairStatus.RESOLVED, resolved_at=datetime.now(timezone.utc))
        db.session.add(case)
        db.session.commit()

        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_analytics_export(client):
    resp = client.post("/api/auth/login", json={"username": "official", "password": "pass"})
    token = resp.get_json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # JSON export
    response = client.get("/api/admin/analytics/export?format=json", headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data["value"] >= 10.0 # ~10 hours downtime
    assert len(data["trends"]) > 0
    assert data["trends"][0]["district"] == "Bo"

    # CSV export
    response = client.get("/api/admin/analytics/export?format=csv", headers=headers)
    assert response.status_code == 200
    assert "text/csv" in response.headers["Content-Type"]
    assert "Reduction in Downtime" in response.get_data(as_text=True)
