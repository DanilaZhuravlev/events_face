# src/events/tasks.py
from celery import shared_task
from .models import Event
from django.utils import timezone
import logging
from datetime import timedelta

logger = logging.getLogger(__name__)

@shared_task
def delete_old_events_task():
    """
    Celery-задача для автоматического удаления мероприятий, закончившихся более 7 дней назад.
    """
    cutoff_date = timezone.now() - timedelta(days=7)
    old_events = Event.objects.filter(event_time__lt=cutoff_date) # Фильтруем мероприятия, у которых event_time меньше, чем cutoff_date
    deleted_count = old_events.count()

    if deleted_count > 0:
        old_events.delete() # Удаляем найденные мероприятия
        logger.info(f"Успешно удалено {deleted_count} устаревших мероприятий, закончившихся до {cutoff_date}.")
        print(f"DEBUG EVENTS TASK: Успешно удалено {deleted_count} устаревших мероприятий, закончившихся до {cutoff_date}.") # Debug print
    else:
        logger.info("Не найдено устаревших мероприятий для удаления.")
        print("DEBUG EVENTS TASK: Не найдено устаревших мероприятий для удаления.") # Debug print