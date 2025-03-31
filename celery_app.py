import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "src.core.settings")

app = Celery("events_face")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=False)
def debug_task(self):
    print(f"Request: {self.request!r}")
    return "debug_task completed"


app.conf.beat_schedule = {
    "delete-old-events-daily": {
        "task": "src.events.tasks.delete_old_events_task",
        "schedule": crontab(hour=3, minute=0),
    },
    "process-expired-pending-registrations": {
        "task": "src.registrations.tasks.process_expired_pending_registrations",
        "schedule": crontab(minute="*/1"),
    },
}
