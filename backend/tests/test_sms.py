import pytest

from app import create_app
from app.extensions import db
from app.models.repair_case import RepairCase
from app.models.report import Report
from app.models.water_source import WaterSource, WaterSourceStatus


@pytest.fixture
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        db.session.add_all(
            [
                WaterSource(
                    id="WELL1",
                    name="Bo Central Well",
                    district="Bo",
                    latitude=7.95,
                    longitude=-11.74,
                    status=WaterSourceStatus.SAFE,
                ),
                WaterSource(
                    id="WELL2",
                    name="Bo East Pump",
                    district="Bo",
                    latitude=7.96,
                    longitude=-11.73,
                    status=WaterSourceStatus.CAUTION,
                ),
            ]
        )
        db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def sms(client, text, from_number="+23276123456"):
    response = client.post(
        "/api/sms/callback",
        json={"from": from_number, "text": text},
    )
    assert response.status_code == 200
    body = response.get_json()["response"]
    assert len(body) <= 160
    return body


def test_sms_status(client):
    body = sms(client, "STATUS WELL1")

    assert "Bo Central Well" in body
    assert "Safe" in body


def test_sms_nearby(client):
    body = sms(client, "NEARBY Bo")

    assert body.startswith("Nearby:")
    assert "WELL1:Bo Central Well" in body
    assert "WELL2:Bo East Pump" in body


def test_sms_cause_creates_anonymous_report_and_repair_case(client):
    body = sms(client, "CAUSE WELL1 BROKEN_PUMP")

    assert "Reported" in body
    report = Report.query.one()
    assert report.source_id == "WELL1"
    assert report.cause_category == "BROKEN_PUMP"
    assert report.reporter_phone_hash
    assert "+23276123456" not in report.reporter_phone_hash
    assert RepairCase.query.count() == 1
    assert db.session.get(WaterSource, "WELL1").status == WaterSourceStatus.UNSAFE


def test_sms_tips(client):
    body = sms(client, "TIPS")

    assert "Tips:" in body
    assert "STATUS <ID>" in body
