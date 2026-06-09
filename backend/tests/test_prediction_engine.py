import pytest
from datetime import datetime, timedelta, timezone

from app import create_app
from app.extensions import db
from app.models.report import Report
from app.models.water_source import WaterSource, WaterSourceStatus
from app.services.prediction_engine import PredictionEngine


@pytest.fixture
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


def test_prediction_engine_warns_and_updates_sources(app, monkeypatch):
    now = datetime.now(timezone.utc)
    db.session.add_all(
        [
            WaterSource(
                id="WELL1",
                name="Bo Central Well",
                district="Bo",
                latitude=7.95,
                longitude=-11.74,
                status=WaterSourceStatus.SAFE,
                committee_phone="+23276123456",
            ),
            WaterSource(
                id="WELL2",
                name="Bo East Pump",
                district="Bo",
                latitude=7.96,
                longitude=-11.73,
                status=WaterSourceStatus.SAFE,
            ),
        ]
    )
    db.session.add_all(
        [
            Report(
                source_id="WELL1",
                reporter_phone_hash="hash1",
                cause_category="DRY_WELL",
                timestamp=now - timedelta(days=2),
            ),
            Report(
                source_id="WELL1",
                reporter_phone_hash="hash2",
                cause_category="DRY_WELL",
                timestamp=now - timedelta(days=5),
            ),
            Report(
                source_id="WELL1",
                reporter_phone_hash="hash3",
                cause_category="DRY_WELL",
                timestamp=now - timedelta(days=10),
            ),
        ]
    )
    db.session.commit()

    engine = PredictionEngine()
    monkeypatch.setattr(engine, "fetch_rainfall", lambda district: 2.0)
    monkeypatch.setattr("app.services.prediction_engine.send_sms", lambda to, message: True)

    sent = engine.check_and_warn("Bo")
    assert sent == 1

    source = db.session.get(WaterSource, "WELL1")
    assert source is not None
    assert source.status == WaterSourceStatus.CAUTION
    assert source.last_tested is not None


def test_prediction_engine_does_not_warn_without_low_rainfall(app, monkeypatch):
    db.session.add(
        WaterSource(
            id="WELL3",
            name="Bo North Well",
            district="Bo",
            latitude=7.95,
            longitude=-11.74,
            status=WaterSourceStatus.SAFE,
            committee_phone="+23276123456",
        )
    )
    db.session.add(
        Report(
            source_id="WELL3",
            reporter_phone_hash="hash4",
            cause_category="DRY_WELL",
            timestamp=datetime.now(timezone.utc) - timedelta(days=3),
        )
    )
    db.session.commit()

    engine = PredictionEngine()
    monkeypatch.setattr(engine, "fetch_rainfall", lambda district: 15.0)
    monkeypatch.setattr("app.services.prediction_engine.send_sms", lambda to, message: True)

    sent = engine.check_and_warn("Bo")
    assert sent == 0
    source = db.session.get(WaterSource, "WELL3")
    assert source.status == WaterSourceStatus.SAFE
