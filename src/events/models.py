from django.db import models
from django.db.models import CASCADE
from django.contrib.auth.models import User
import uuid

class EventLocation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Event(models.Model):
    class EventStatus(models.TextChoices):
        OPEN = 'open', 'Мероприятие открыто'
        CLOSED = 'closed', 'Мероприятие закрыто'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    event_time = models.DateTimeField()
    registration_deadline = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=10,
        choices=EventStatus.choices,
        default=EventStatus.OPEN,
    )
    location = models.ForeignKey( # Внешний ключ, связывающий мероприятие с площадкой
        EventLocation, # Ссылка на модель EventLocation
        on_delete=models.SET_NULL, # Что делать при удалении связанной площадки: установить значение в NULL
        null=True, # Разрешить значение NULL (площадка может быть не указана)
        blank=True, # Разрешить пустое значение в формах Django
        related_name='events' # Имя для обратной связи от EventLocation к Event (location.events.all())
    )
    def __str__(self):
        return self.name