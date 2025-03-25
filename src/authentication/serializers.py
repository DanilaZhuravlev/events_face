# src/authentication/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

class RegistrationSerializer(serializers.ModelSerializer):
    """Сериализатор для регистрации нового пользователя."""
    password = serializers.CharField(write_only=True, validators=[validate_password]) # Поле пароля, только для записи, с валидацией

    class Meta:
        model = User
        fields = ('username', 'password')

    def create(self, validated_data):
        """Создание нового пользователя."""
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )
        return user

class LoginSerializer(serializers.Serializer):
    """Сериализатор для входа пользователя."""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

class RefreshTokenSerializer(serializers.Serializer):
    """Сериализатор для обновления Access Token."""
    refresh = serializers.CharField()