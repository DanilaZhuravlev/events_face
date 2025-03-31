# src/registrations/serializers.py
from django.contrib.auth import get_user_model
from rest_framework import serializers

from src.events.serializers import EventSerializer

from .models import Registration

User = get_user_model()


class RegistrationResponseSerializer(serializers.ModelSerializer):
    """Сериализатор для представления данных о регистрации."""

    user_username = serializers.CharField(source="user.username", read_only=True)
    event = EventSerializer(read_only=True)

    class Meta:
        model = Registration
        fields = ["id", "user", "user_username", "event", "registration_time", "status"]
        read_only_fields = [
            "id",
            "registration_time",
            "status",
            "user_username",
            "event",
        ]
