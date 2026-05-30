import pytest
from app import create_app
from app.extensions import db
from app.models.user import User, UserRole

@pytest.fixture
def app():
    app = create_app("testing")

    with app.app_context():
        db.create_all()
        # Seed users
        official = User(username="official", role=UserRole.DISTRICT_OFFICIAL)
        official.set_password("pass")
        tech = User(username="tech", role=UserRole.TECHNICAL_TEAM)
        tech.set_password("pass")
        committee = User(username="committee", role=UserRole.WATER_COMMITTEE_HEAD)
        committee.set_password("pass")
        db.session.add_all([official, tech, committee])
        db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def get_token(client, username, password):
    response = client.post("/api/auth/login", json={"username": username, "password": password})
    return response.get_json()["access_token"]

def test_rbac_analytics_access(client):
    token = get_token(client, "official", "pass")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/admin/analytics/metrics", headers=headers)
    assert response.status_code == 200

    token = get_token(client, "tech", "pass")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/admin/analytics/metrics", headers=headers)
    assert response.status_code == 403

def test_rbac_repairs_access(client):
    token = get_token(client, "tech", "pass")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/admin/repairs", headers=headers)
    assert response.status_code == 200

    token = get_token(client, "committee", "pass")
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/admin/repairs", headers=headers)
    assert response.status_code == 403
