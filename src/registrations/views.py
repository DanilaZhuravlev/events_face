# src/registrations/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from src.notifications.tasks import send_notification
from .tasks import async_register_user_for_event
import uuid, json


class EventRegistrationViewSet(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, event_id):
        if not self._is_valid_uuid(event_id):
            return Response({"error": "Неверный формат ID мероприятия."},
                            status=status.HTTP_400_BAD_REQUEST)

        result = async_register_user_for_event.delay(request.user.id, event_id).get(timeout=10, propagate=False)

        if result and result.get("success"):
            send_notification.delay(
                user_id=request.user.id,
                message="Вы успешно зарегистрированы на мероприятие!",
                notification_type="registration_success"
            )
            return Response({
                "message": "Ваша заявка на регистрацию принята и находится в обработке. "
                           "Статус регистрации будет обновлен в течение часа.",
                "registration_details": json.loads(result.get("registration_data"))
            }, status=status.HTTP_202_ACCEPTED)

        error_message = result.get("error_message", "Произошла ошибка при регистрации.")
        error_status = result.get("status_code", status.HTTP_400_BAD_REQUEST)

        send_notification.delay(
            user_id=request.user.id,
            message=f"Ошибка регистрации на мероприятие: {error_message}",
            notification_type="registration_failure"
        )
        return Response({"error": error_message}, status=error_status)

    @staticmethod
    def _is_valid_uuid(uuid_str):
        try:
            uuid.UUID(str(uuid_str))
            return True
        except ValueError:
            return False