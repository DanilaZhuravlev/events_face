# src/registrations/tasks.py
from celery import shared_task
from rest_framework import status
from django.db import transaction
from django.utils import timezone
from src.events.models import Event
from src.notifications.tasks import send_notification
from .models import Registration
from .serializers import RegistrationResponseSerializer
import json, logging

logger = logging.getLogger(__name__)


@shared_task
@transaction.atomic
def async_register_user_for_event(user_id, event_id):
    try:
        event = Event.objects.get(pk=event_id, status=Event.EventStatus.OPEN)

        if event.registration_deadline and event.registration_deadline < timezone.now():
            return _handle_registration_error(user_id, "Время регистрации истекло.",
                                              "registration_failure_deadline_expired", status.HTTP_400_BAD_REQUEST)

        if Registration.objects.filter(user_id=user_id, event=event).exists():
            return _handle_registration_error(user_id, "Вы уже зарегистрированы.",
                                              "registration_failure_already_registered", status.HTTP_400_BAD_REQUEST)

        registration = Registration.objects.create(user_id=user_id, event=event)
        async_confirm_registration.apply_async(args=[registration.id], countdown=3600)

        return {
            "success": True,
            "registration_data": json.dumps(RegistrationResponseSerializer(registration).data),
            "status_code": status.HTTP_201_CREATED
        }

    except Event.DoesNotExist:
        return _handle_registration_error(user_id, "Мероприятие не найдено.",
                                          "registration_failure_event_not_found", status.HTTP_404_NOT_FOUND)


@shared_task
@transaction.atomic
def async_confirm_registration(registration_id):
    try:
        registration = Registration.objects.get(pk=registration_id, status='pending')
        is_expired = registration.event.registration_deadline and registration.event.registration_deadline < timezone.now()

        registration.status = 'rejected' if is_expired else 'confirmed'
        registration.save()

        message = "К сожалению, ваша регистрация отклонена." if is_expired else "Регистрация подтверждена!"
        notification_type = "registration_rejected" if is_expired else "registration_confirmed"

        send_notification.delay(user_id=registration.user.id, message=message, notification_type=notification_type)
        logger.info(f"Регистрация {registration_id} обработана. Статус: {registration.status}")

    except Exception as e:
        logger.error(f"Ошибка обработки регистрации {registration_id}: {e}")


def _handle_registration_error(user_id, message, notification_type, status_code):
    send_notification.delay(user_id=user_id, message=f"Ошибка регистрации: {message}",
                            notification_type=notification_type)
    return {"success": False, "error_message": message, "status_code": status_code}