import os
from celery import Celery

def make_celery():
    broker = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")
    backend = os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/1")

    celery = Celery(
        "ec2_nonprod_stopper",
        broker=broker,
        backend=backend,
        include=["app.tasks"]
    )

    celery.conf.update(
        timezone=os.getenv("TZ", "Asia/Kolkata"),
        enable_utc=False,
        task_track_started=True
    )
    return celery

celery = make_celery()
