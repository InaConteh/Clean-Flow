import pytest
from app import create_app
from app.extensions import db
from app.models.water_source import WaterSource, WaterSourceStatus
from app.models.report import Report
from app.models.repair_case import RepairCase, RepairStatus
from app.models.user import User, UserRole

@pytest.fixture
def app():
    app = create_app("development")
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "JWT_SECRET_KEY": "test-secret-long-enough-for-security-reasons-123"
    })
    with app.app_context():
        db.create_all()
        # Seed
        official = User(username="official", role=UserRole.DISTRICT_OFFICIAL)
        official.set_password("pass")
        source = WaterSource(id="WELL1", name="Well 1", latitude=0.0, longitude=0.0, status=WaterSourceStatus.SAFE)
        db.session.add_all([official, source])
        db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_repair_lifecycle(client):
    # 1. Create Report (triggers Red status and Reported case)
    client.post("/api/report", json={"source_id": "WELL1", "cause_category": "BROKEN_PUMP"})

    source = WaterSource.query.get("WELL1")
    assert source.status == WaterSourceStatus.UNSAFE

    case = RepairCase.query.first()
    assert case.status == RepairStatus.REPORTED

    # 2. Login as Official to advance case
    resp = client.post("/api/auth/login", json={"username": "official", "password": "pass"})
    token = resp.get_json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Advance to ASSIGNED
    client.patch(f"/api/admin/repairs/{case.id}", json={"status": RepairStatus.ASSIGNED}, headers=headers)
    case = RepairCase.query.get(case.id)
    assert case.status == RepairStatus.ASSIGNED

    # 4. Advance to RESOLVED
    client.patch(f"/api/admin/repairs/{case.id}", json={"status": RepairStatus.RESOLVED}, headers=headers)
    case = RepairCase.query.get(case.id)
    assert case.status == RepairStatus.RESOLVED
    assert case.resolved_at is not None

    source = WaterSource.query.get("WELL1")
    assert source.status == WaterSourceStatus.SAFE
