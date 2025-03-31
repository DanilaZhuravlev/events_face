# src/events/views.py
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.pagination import PageNumberPagination

from .models import Event
from .serializers import EventSerializer


class EventPagination(PageNumberPagination):
    """Класс пагинации для эндпоинта событий."""

    page_size = 10  # Размер страницы по умолчанию - 10 мероприятий
    page_size_query_param = (
        "page_size"  # Имя параметра запроса для изменения размера страницы
    )
    max_page_size = 100  # Максимально допустимый размер страницы


class EventViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для просмотра списка мероприятий."""

    queryset = Event.objects.filter(status=Event.EventStatus.OPEN).prefetch_related(
        "location"
    )  # Queryset для получения открытых мероприятий
    serializer_class = EventSerializer
    filter_backends = [
        filters.SearchFilter,
        filters.OrderingFilter,
        DjangoFilterBackend,
    ]  # Подключаем бэкенды фильтрации
    search_fields = [
        "name"
    ]  # Поля, по которым будет осуществляться поиск (полнотекстовый поиск по названию)
    ordering_fields = [
        "event_time"
    ]  # Поля, по которым разрешена сортировка (по дате проведения)
    pagination_class = EventPagination  # Подключаем класс пагинации
    filterset_fields = [
        "status",
        "registration_deadline",
    ]  # Поля, по которым разрешена фильтрация через DjangoFilterBackend (в данном случае, статус)

    def get_queryset(self):
        """Переопределяем queryset для дополнительной логики (если потребуется)."""
        queryset = (
            super().get_queryset()
        )  # Получаем базовый queryset из родительского класса
        return queryset
