import logging
import uuid

from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from src.events.models import Event

from .tasks import async_register_user_for_event

logger = logging.getLogger(__name__)


class EventRegistrationViewSet(APIView):
    """
    API View для регистрации пользователя на мероприятие.
    Запускает асинхронную задачу Celery для обработки регистрации.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, event_id):
        """
        Обрабатывает POST-запрос для регистрации на мероприятие.
        Выполняет базовые проверки и ставит задачу в очередь Celery.
        """
        user = request.user
        logger.info(
            f"Пользователь {user.id} пытается зарегистрироваться на событие {event_id}"
        )

        try:
            event_uuid = uuid.UUID(str(event_id))
        except ValueError:
            logger.warning(f"Неверный формат UUID {event_id} от пользователя {user.id}")
            return Response(
                {"error": "Неверный формат ID мероприятия."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            event = Event.objects.get(pk=event_uuid, status=Event.EventStatus.OPEN)
        except Event.DoesNotExist:
            logger.warning(
                f"Событие {event_uuid} не найдено или закрыто для регистрации (запрос от user {user.id})"
            )
            return Response(
                {"error": "Мероприятие не найдено или закрыто для регистрации."},
                status=status.HTTP_404_NOT_FOUND,
            )
        if event.registration_deadline and event.registration_deadline < timezone.now():
            logger.warning(
                f"Дедлайн регистрации на событие {event_uuid} прошел (запрос от user {user.id})"
            )
            return Response(
                {"error": f"Время регистрации на мероприятие '{event.name}' истекло."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            task_result = async_register_user_for_event.delay(user.id, str(event_uuid))
            logger.info(
                f"Задача регистрации user {user.id} на event {event_uuid} успешно поставлена в очередь, task_id: {task_result.id}"
            )
            return Response(
                {
                    "message": "Ваша заявка на регистрацию принята в обработку. "
                    "Вы получите уведомление о результате в ближайшее время.",
                    "task_id": task_result.id,
                },
                status=status.HTTP_202_ACCEPTED,
            )
        except Exception as e:
            logger.error(
                f"Не удалось поставить задачу регистрации user {user.id} на event {event_uuid} в очередь: {e}",
                exc_info=True,
            )
            return Response(
                {
                    "error": "Не удалось начать процесс регистрации. Пожалуйста, попробуйте позже."
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
