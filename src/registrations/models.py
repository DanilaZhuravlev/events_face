from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone

from src.events.models import Event


# Определяем именованную функцию для значения по умолчанию expires_at
def get_default_expires_at():
    return timezone.now() + timedelta(hours=1)


# --------------------


class Registration(models.Model):
    """Модель для регистрации посетителей на мероприятия."""

    STATUS_CHOICES = [
        ("pending", "В ожидании"),
        ("confirmed", "Подтверждена"),
        ("rejected", "Отклонена"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="registrations",
        verbose_name="Посетитель",
    )
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="registrations",
        verbose_name="Мероприятие",
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Время создания регистрации"
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Время последнего обновления"
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="pending",
        db_index=True,
        verbose_name="Статус регистрации",
    )
    expires_at = models.DateTimeField(
        default=get_default_expires_at,
        # ------------------------
        db_index=True,
        verbose_name="Истекает в",
        help_text="Время, после которого ожидающая регистрация будет автоматически отклонена, если статус не изменится",
    )

    class Meta:
        unique_together = ("user", "event")
        verbose_name = "Регистрация"
        verbose_name_plural = "Регистрации"
        ordering = ["-created_at"]

    def __str__(self):
        user_repr = getattr(self.user, "username", self.user.id)
        event_repr = getattr(self.event, "name", self.event.id)
        return f"Регистрация {user_repr} на {event_repr} ({self.get_status_display()})"
