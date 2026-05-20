"""Celery tasks for async SMS broadcasts and prediction runs."""

from celery import Celery

celery_app = Celery("cleanflow")


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
def run_drought_check(district: str, phone_numbers: list[str]):
    from app.services.prediction_engine import PredictionEngine

    engine = PredictionEngine()
    if engine.should_warn(district):
        return engine.broadcast_warning(district, phone_numbers)
    return 0
