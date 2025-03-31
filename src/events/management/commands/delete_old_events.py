# src/events/management/commands/delete_old_events.py
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from src.events.models import Event


class Command(BaseCommand):
    help = "Удаление мероприятий, закончившихся более 7 дней назад"

    def handle(self, *args, **options):
        """Логика удаления устаревших мероприятий."""
        cutoff_date = timezone.now() - timedelta(
            days=7
        )  # Определяем дату отсечения (7 дней назад от текущей даты)
        old_events = Event.objects.filter(
            event_time__lte=cutoff_date
        )  # Выбираем мероприятия, event_time которых раньше или равна дате отсечения
        deleted_count = (
            old_events.count()
        )  # Получаем количество устаревших мероприятий перед удалением

        if deleted_count > 0:
            old_events.delete()
            self.stdout.write(
                self.style.SUCCESS(
                    f"Успешно удалено {deleted_count} устаревших мероприятий, закончившихся до {cutoff_date.strftime('%d.%m.%Y')}"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    "Нет устаревших мероприятий для удаления."
                )  # Сообщение об отсутствии устаревших мероприятий
            )
