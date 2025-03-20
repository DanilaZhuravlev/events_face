from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken, TokenError # Убрали импорт BlacklistError
from .serializers import RegistrationSerializer, LoginSerializer, RefreshTokenSerializer

class RegistrationView(GenericAPIView):
    """Регистрация пользователя."""
    serializer_class = RegistrationSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        tokens = self._get_tokens_for_user(user)
        return Response({
            'message': 'User created successfully',
            'data': tokens
        }, status=status.HTTP_201_CREATED)

    @staticmethod
    def _get_tokens_for_user(user):
        """Создает пару access и refresh токенов для пользователя."""
        refresh = RefreshToken.for_user(user)
        return {
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
        }


class LoginView(GenericAPIView):
    """Аутентификация пользователя и получение токенов."""
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            username=serializer.validated_data['username'],
            password=serializer.validated_data['password']
        )
        if not user:
            return Response({'error': 'Invalid username or password'}, status=status.HTTP_401_UNAUTHORIZED)

        tokens = RegistrationView._get_tokens_for_user(user) # Переиспользуем метод генерации токенов
        return Response({
            'message': 'Login successful',
            'data': tokens
        }, status=status.HTTP_200_OK)


class RefreshTokenView(GenericAPIView):
    """Обновление Access Token с использованием Refresh Token."""
    serializer_class = RefreshTokenSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self._refresh_access_token(serializer.validated_data['refresh'])

    @staticmethod
    def _refresh_access_token(refresh_token: str) -> Response:
        """Обновляет Access Token, если Refresh Token валиден."""
        try:
            refresh = RefreshToken(refresh_token)
            return Response({'access_token': str(refresh.access_token)}, status=status.HTTP_200_OK)
        except TokenError:
            return Response({'error': 'Invalid or expired refresh token'}, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(GenericAPIView):
    """Выход пользователя (аннулирование Refresh Token)."""
    serializer_class = RefreshTokenSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return self._invalidate_refresh_token(serializer.validated_data['refresh'])

    @staticmethod
    def _invalidate_refresh_token(refresh_token: str) -> Response:
        """Добавляет Refresh Token в черный список."""
        try:
            refresh = RefreshToken(refresh_token)
            refresh.blacklist()
            return Response({'message': 'Successfully logged out'}, status=status.HTTP_205_RESET_CONTENT)
        except TokenError:
            return Response({'error': 'Invalid refresh token'}, status=status.HTTP_400_BAD_REQUEST)