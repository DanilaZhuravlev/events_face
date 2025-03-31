# src/sync/admin.py
from django.contrib import admin

from .models import SyncHistory

admin.site.register(SyncHistory)
