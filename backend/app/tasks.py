"""Celery tasks for async SMS broadcasts and prediction runs."""

from celery import Celery

from app.extensions import db
from app.models.water_source import WaterSource

celery_app = Celery("cleanflow")
celery_app.conf.beat_schedule = {
    "drought-check-every-hour": {
        "task": "app.tasks.check_all_districts_for_drought",
        "schedule": 3600.0,
    }
}


def init_celery(flask_app):
    celery_app.conf.update(
        broker_url=flask_app.config["CELERY_BROKER_URL"],
        result_backend=flask_app.config["CELERY_RESULT_BACKEND"],
    )
    celery_app.conf.update(flask_app.config)

    class ContextTask(celery_app.Task):
        def __call__(self, *args, **kwargs):
            with flask_app.app_context():
                return self.run(*args, **kwargs)

    celery_app.Task = ContextTask
    return celery_app


@celery_app.task
def run_drought_check(district: str, phone_numbers: list[str] | None = None):
    from app.services.prediction_engine import PredictionEngine

    engine = PredictionEngine()
    if engine.should_warn(district):
        if phone_numbers is None:
            phone_numbers = engine.collect_phone_numbers(district)
        return engine.broadcast_warning(district, phone_numbers)
    return 0


@celery_app.task
def check_all_districts_for_drought():
    from app.services.prediction_engine import PredictionEngine

    engine = PredictionEngine()
    districts = [row[0] for row in db.session.query(WaterSource.district)
                 .filter(WaterSource.district.isnot(None))
                 .distinct()]
    count = 0
    for district in districts:
        count += engine.check_and_warn(district)
    return count


@celery_app.task
def send_maintenance_reminders():
    """Send routine maintenance reminders to Water Committee Heads."""
    from app.models.water_source import WaterSource
    from app.services.notification_service import NotificationService
    from app.services.sms_gateway import send_sms

    notifier = NotificationService()
    sources = WaterSource.query.filter(WaterSource.committee_phone.isnot(None)).all()

    count = 0
    for source in sources:
        message = notifier.get_maintenance_reminder(
            source_name=source.name,
            language=source.preferred_language
        )
        if send_sms(source.committee_phone, message):
            count += 1

    return count
