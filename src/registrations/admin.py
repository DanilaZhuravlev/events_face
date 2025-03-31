# src/registrations/admin.py
from django.contrib import admin

from .models import Registration


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "event",
        "registration_time",
        "status",
    )  # Отображаем поля в списке регистраций
    list_filter = (  # Добавляем фильтры на боковой панели
        "status",
        "event",
        "user__username",
        "user__email",  # (связанная модель User)
        "registration_time",
    )
    search_fields = (
        "user__username",
        "user__email",
        "event__name",
    )  # Добавляем поиск по полям пользователя и мероприятия
