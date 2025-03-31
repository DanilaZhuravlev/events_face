from django.contrib import admin

# Импортируем вашу модель Registration
from .models import Registration


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "event",
        "status",
        "created_at",
        "expires_at",
        "updated_at",
    )

    # Поля, по которым можно будет фильтровать список на боковой панели
    list_filter = (
        "status",
        "event",
        "created_at",
        "expires_at",
    )

    search_fields = (
        "id__iexact",  # Поиск по точному ID (UUID)
        "user__username",
        "user__email",
        "event__name",
    )

    # Поля, которые будут доступны только для чтения в форме редактирования
    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
    )
