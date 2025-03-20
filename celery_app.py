# events-face/celery_app.py
import os
from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.core.settings')

app = Celery('events_face')
app.config_from_object('django.conf:settings', namespace='CELERY')


app.autodiscover_tasks()

@app.task(bind=True, ignore_result=False)
def debug_task(self):
    print(f'Request: {self.request!r}')
    return 'debug_task completed'