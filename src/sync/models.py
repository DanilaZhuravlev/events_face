# src/sync/models.py
from django.db import models

class SyncHistory(models.Model):
    """Модель для хранения истории синхронизаций мероприятий."""
    date = models.DateTimeField(auto_now_add=True, verbose_name='Дата синхронизации')
    new_events_count = models.PositiveIntegerField(default=0, verbose_name='Новых мероприятий')
    updated_events_count = models.PositiveIntegerField(default=0, verbose_name='Обновленных мероприятий')

    class Meta:
        verbose_name = 'История синхронизации'
        verbose_name_plural = 'История синхронизаций'
        ordering = ['-date']

    def __str__(self):
        """Строковое представление объекта SyncHistory."""
        return f"Синхронизация от {self.date.strftime('%d.%m.%Y %H:%M:%S')}"