from django.urls import path

from .views import EventRegistrationViewSet

urlpatterns = [
    path(
        "events/<uuid:event_id>/register/",
        EventRegistrationViewSet.as_view(),
        name="event_registration",
    ),
]
