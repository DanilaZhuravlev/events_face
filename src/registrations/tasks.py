import logging

from celery import shared_task
from django.db import IntegrityError, transaction
from django.utils import timezone

from src.events.models import Event
from src.notifications.tasks import send_notification

from .models import Registration

logger = logging.getLogger(__name__)


def _handle_registration_error(user_id, message, notification_type):
    """Отправляет уведомление об ошибке и возвращает словарь ошибки"""
    try:
        send_notification.delay(
            user_id=user_id,
            message=f"Ошибка регистрации: {message}",
            notification_type=notification_type,
        )
    except Exception as e:
        logger.error(
            f"Не удалось отправить уведомление об ошибке ({notification_type}) пользователю {user_id}: {e}",
            exc_info=True,
        )
    return {"success": False, "error_message": message}


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def async_register_user_for_event(self, user_id, event_id):
    """Асинхронно регистрирует пользователя на мероприятие"""
    try:
        event = Event.objects.filter(pk=event_id, status=Event.EventStatus.OPEN).first()

        if not event:
            logger.warning(
                f"Событие {event_id} не найдено или закрыто (user {user_id})"
            )
            return _handle_registration_error(
                user_id,
                "Мероприятие не найдено или закрыто.",
                "registration_failure_event_not_found",
            )

        if event.registration_deadline and event.registration_deadline < timezone.now():
            logger.warning(f"Дедлайн регистрации на {event_id} прошел (user {user_id})")
            return _handle_registration_error(
                user_id,
                f"Время регистрации на '{event.name}' истекло.",
                "registration_failure_deadline_expired",
            )

        registration, created = Registration.objects.get_or_create(
            user_id=user_id, event=event
        )

        if not created:
            logger.warning(f"Пользователь {user_id} уже зарегистрирован на {event_id}.")
            return _handle_registration_error(
                user_id,
                f"Вы уже зарегистрированы на '{event.name}'.",
                "registration_failure_already_registered",
            )
        else:
            logger.info(
                f"Создана регистрация {registration.id} (pending) для user {user_id} на event {event_id}."
            )
            try:
                send_notification.delay(
                    user_id=user_id,
                    message=f"Ваша заявка на регистрацию на '{event.name}' принята.",
                    notification_type="registration_pending",
                )
            except Exception as notify_err:
                logger.error(
                    f"Ошибка отправки pending уведомления для {registration.id}: {notify_err}",
                    exc_info=True,
                )

            return {
                "success": True,
                "message": "Заявка принята.",
                "registration_id": registration.id,
            }

    except IntegrityError as ie:
        logger.error(
            f"Ошибка IntegrityError при регистрации user {user_id} на event {event_id}: {ie}",
            exc_info=True,
        )
        try:
            self.retry(exc=ie)
        except self.MaxRetriesExceededError:
            return _handle_registration_error(
                user_id,
                "Ошибка базы данных при регистрации.",
                "registration_failure_db",
            )
    except Exception as e:
        logger.error(
            f"Критическая ошибка при регистрации user {user_id} на event {event_id}: {e}",
            exc_info=True,
        )
        try:
            self.retry(exc=e)
        except self.MaxRetriesExceededError:
            return _handle_registration_error(
                user_id,
                "Произошла внутренняя ошибка сервера.",
                "registration_failure_server_error",
            )


@shared_task(name="src.registrations.tasks.process_expired_pending_registrations")
def process_expired_pending_registrations():
    now = timezone.now()
    logger.info(f"Запуск process_expired_pending_registrations в {now}")

    expired_ids = Registration.objects.filter(
        status="pending", expires_at__lte=now
    ).values_list("id", flat=True)

    expired_count = expired_ids.count()
    if expired_count == 0:
        logger.info("Не найдено просроченных ожидающих регистраций.")
        return "No expired pending registrations found."

    logger.info(f"Найдено {expired_count} просроченных регистраций для обработки.")
    processed_count = 0
    failed_count = 0

    for reg_id in expired_ids.iterator():
        try:
            with transaction.atomic():
                registration = (
                    Registration.objects.select_related("event")
                    .select_for_update()
                    .get(pk=reg_id, status="pending")
                )

                if registration.expires_at > now:
                    logger.warning(
                        f"Регистрация {reg_id} еще не истекла при блокировке ({registration.expires_at}). Пропуск."
                    )
                    continue

                registration.status = "rejected"
                registration.save(update_fields=["status", "updated_at"])

            try:
                send_notification.delay(
                    user_id=registration.user_id,
                    message=f"Ваша заявка на регистрацию на '{registration.event.name}' отклонена (истекло время).",
                    notification_type="registration_rejected_timeout",
                )
                processed_count += 1
                logger.info(f"Регистрация {reg_id} успешно отклонена.")
            except Exception as notify_exc:
                logger.error(
                    f"Ошибка отправки уведомления об отклонении для {reg_id}: {notify_exc}",
                    exc_info=True,
                )
                processed_count += 1

        except Registration.DoesNotExist:
            logger.warning(
                f"Регистрация {reg_id} не найдена со статусом 'pending' при попытке блокировки."
            )
        except Exception as e:
            logger.error(
                f"Ошибка при автоматическом отклонении регистрации {reg_id}: {e}",
                exc_info=True,
            )
            failed_count += 1

    result_message = f"Завершено process_expired_pending_registrations. Успешно отклонено: {processed_count}, Ошибки/пропущено: {failed_count}."
    logger.info(result_message)
    return result_message
