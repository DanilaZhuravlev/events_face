import logging
import time

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_notification(self, user_id, message, notification_type):
    """
    Асинхронная задача для отправки уведомлений.

    Args:
        user_id (int): ID пользователя, которому отправляется уведомление.
        message (str): Текст уведомления.
        notification_type (str): Тип уведомления (для логирования).
    """
    try:
        # Имитируем отправку (можно заменить на реальный сервис)
        print(
            f"DEBUG NOTIFICATIONS TASK: Отправка уведомления типа '{notification_type}' пользователю {user_id}: {message}"
        )
        logger.info(
            f"Отправка уведомления типа '{notification_type}' пользователю {user_id}: {message}"
        )
        time.sleep(2)  # Имитируем задержку
        print(
            f"DEBUG NOTIFICATIONS TASK: Уведомление типа '{notification_type}' пользователю {user_id} успешно отправлено."
        )
        logger.info(
            f"Уведомление типа '{notification_type}' пользователю {user_id} успешно отправлено."
        )

    except Exception as exc:
        logger.exception(
            f"Ошибка при отправке уведомления типа '{notification_type}' пользователю {user_id}. Повторная попытка. Ошибка: {exc}"
        )
        self.retry(exc=exc, countdown=10)
