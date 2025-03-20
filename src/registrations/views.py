# src/registrations/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .serializers import RegistrationResponseSerializer
from src.events.models import Event
from .models import Registration
import uuid

class EventRegistrationViewSet(APIView):
    """ViewSet для регистрации на мероприятие."""
    permission_classes = [IsAuthenticated]

    def post(self, request, event_id):
        """Регистрация пользователя на мероприятие."""
        try:
            uuid.UUID(str(event_id))
        except ValueError:
            return Response({"error": "Неверный формат ID мероприятия."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            event = Event.objects.get(pk=event_id, status=Event.EventStatus.OPEN)
        except Event.DoesNotExist:
            return Response({"error": "Мероприятие не найдено или закрыто для регистрации."}, status=status.HTTP_404_NOT_FOUND)

        if Registration.objects.filter(user=request.user, event=event).exists():
            return Response({"error": "Вы уже зарегистрированы на это мероприятие."}, status=status.HTTP_400_BAD_REQUEST)

        registration = Registration.objects.create(user=request.user, event=event)
        response_serializer = RegistrationResponseSerializer(registration)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)