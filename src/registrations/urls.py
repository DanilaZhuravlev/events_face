# src/registrations/urls.py
from django.urls import path
from .views import EventRegistrationViewSet

urlpatterns = [
    path('src.events/<uuid:event_id>/register/', EventRegistrationViewSet.as_view(), name='event_registration'), # <-- ИЗМЕНЕНО: 'src.events/' вместо 'events/'
]