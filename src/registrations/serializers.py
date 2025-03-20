# src/registrations/serializers.py
from rest_framework import serializers
from .models import Registration
from src.events.serializers import EventSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

class RegistrationResponseSerializer(serializers.ModelSerializer):
    """Сериализатор для представления данных о регистрации."""
    user_username = serializers.CharField(source='user.username', read_only=True)
    event = EventSerializer(read_only=True)

    class Meta:
        model = Registration
        fields = ['id', 'user', 'user_username', 'event', 'registration_time', 'status']
        read_only_fields = ['id', 'registration_time', 'status', 'user_username', 'event']