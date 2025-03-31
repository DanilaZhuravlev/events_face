from django.contrib import admin

from .models import Event, EventLocation

admin.site.register(Event)
admin.site.register(EventLocation)
