# src/events/serializers.py
from rest_framework import serializers
from .models import Event, EventLocation

class EventLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventLocation
        fields = ['id', 'name']

class EventSerializer(serializers.ModelSerializer):
    location_name = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = ['id', 'name', 'event_time', 'registration_deadline', 'status', 'location', 'location_name']

    def get_location_name(self, obj):
        if obj.location:
            return obj.location.name
        return None