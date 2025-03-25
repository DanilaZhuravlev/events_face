# events-face/celery_app.py
import os
from celery import Celery
from celery.schedules import crontab


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.core.settings')
os.environ['FORKED_BY_MULTIPROCESSING'] = '1'
app = Celery('events_face')
app.config_from_object('django.conf:settings', namespace='CELERY')


app.autodiscover_tasks()

@app.task(bind=True, ignore_result=False)
def debug_task(self):
    print(f'Request: {self.request!r}')
    return 'debug_task completed'

# *** Добавляем конфигурацию Celery Beat для расписания задач ***
app.conf.beat_schedule = {
    'delete-old-events-daily': { # Уникальное имя для задачи в расписании
        'task': 'src.events.tasks.delete_old_events_task', # Полный путь к Celery task
        'schedule': crontab(hour=3, minute=0), # Запускать ежедневно в 3:00 утра
        # 'schedule': crontab(minute='*/1'), # *** Для тестирования, проверка для удаления и запуска задачи каждую минуту
    },
}