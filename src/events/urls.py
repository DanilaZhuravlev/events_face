# src/events/urls.py
from django.urls import include, path  # Импортируем path и include из django.urls
from rest_framework.routers import DefaultRouter  # Импортируем DefaultRouter из DRF

from .views import EventViewSet  # Импортируем EventViewSet из views.py

router = DefaultRouter()
router.register("src.events", EventViewSet, basename="event")

urlpatterns = [
    path("", include(router.urls)),
]
