# src/registrations/models.py
from django.db import models
from django.conf import settings
from src.events.models import Event

class Registration(models.Model):
    """Модель для регистрации посетителей на мероприятия."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='registrations', verbose_name='Посетитель') # ForeignKey на модель User
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations', verbose_name='Мероприятие') # ForeignKey на модель Event
    registration_time = models.DateTimeField(auto_now_add=True, verbose_name='Время регистрации') # Дата и время регистрации
    status = models.CharField( # Статус регистрации
        max_length=20,
        default='pending', # По умолчанию статус "pending" (в ожидании)
        choices=[
            ('pending', 'В ожидании'),
            ('confirmed', 'Подтверждена'),
            ('rejected', 'Отклонена'),
        ],
        verbose_name='Статус регистрации'
    )

    class Meta:
        unique_together = ('user', 'event')
        verbose_name = 'Регистрация'
        verbose_name_plural = 'Регистрации'
        ordering = ['-registration_time']

    def __str__(self):
        """Строковое представление объекта Registration."""
        return f"Регистрация пользователя {self.user.username} на мероприятие {self.event.name} ({self.get_status_display()})"