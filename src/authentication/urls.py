# src/authentication/urls.py
from django.urls import path

from .views import LoginView, LogoutView, RefreshTokenView, RegistrationView

urlpatterns = [
    path("register/", RegistrationView.as_view(), name="auth_register"),
    path("login/", LoginView.as_view(), name="auth_login"),
    path("token/refresh/", RefreshTokenView.as_view(), name="token_refresh"),
    path("logout/", LogoutView.as_view(), name="auth_logout"),
]
