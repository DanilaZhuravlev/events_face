# src/authentication/urls.py
from django.urls import path
from .views import RegistrationView, LoginView, RefreshTokenView, LogoutView

urlpatterns = [
    path('register/', RegistrationView.as_view(), name='auth_register'), # URL для регистрации
    path('login/', LoginView.as_view(), name='auth_login'), # URL для входа
    path('token/refresh/', RefreshTokenView.as_view(), name='token_refresh'), # URL для обновления токена
    path('logout/', LogoutView.as_view(), name='auth_logout'), # URL для выхода
]