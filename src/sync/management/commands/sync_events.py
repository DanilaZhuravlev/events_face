import requests
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from src.events.models import Event, EventLocation
from src.sync.models import SyncHistory

class Command(BaseCommand):
    help = "Sync events from events-provider"

    def add_arguments(self, parser):
        parser.add_argument('--date', type=str, help='Date in YYYY-MM-DD format')
        parser.add_argument('--all', action='store_true', help='Sync all events')

    def handle(self, *args, **options):
        api_url = "https://events.k3scluster.tech/api/events/"

        if options['all']:
            sync_date = timezone.now().date()
            self.stdout.write(self.style.WARNING("Начало полной синхронизации всех мероприятий..."))
        elif options['date']:
            try:
                sync_date = datetime.strptime(options['date'], "%Y-%m-%d").date()
                api_url += f"?changed_at={sync_date:%Y-%m-%d}"
                self.stdout.write(self.style.WARNING(f"Синхронизация мероприятий за {sync_date}"))
            except ValueError:
                self.stderr.write(self.style.ERROR("Неверный формат даты. Используйте: YYYY-MM-DD"))
                return
        else:
            sync_date = timezone.now().date() - timedelta(days=1)
            api_url += f"?changed_at={sync_date:%Y-%m-%d}"
            self.stdout.write(self.style.WARNING(f"Синхронизация вчерашних мероприятий ({sync_date})"))

        response = requests.get(api_url)
        if response.status_code != 200:
            self.stderr.write(self.style.ERROR(f"API request failed: {response.status_code}"))
            return

        try:
            events_data = response.json().get("results", [])
            stats = self.process_events(events_data)

            SyncHistory.objects.create(
                date=timezone.now(),
                new_events_count=stats['new'],
                updated_events_count=stats['updated']
            )

            self.stdout.write(self.style.SUCCESS(f"Синхронизация завершена: {stats['new']} новых, {stats['updated']} обновлено"))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error: {str(e)}"))

    def process_events(self, events_data):
        stats = {'new': 0, 'updated': 0}

        for event in events_data:
            try:
                location = None
                if event.get('location'):
                    location, _ = EventLocation.objects.get_or_create(name=event['location'])

                obj, created = Event.objects.update_or_create(
                    id=event['id'],
                    defaults={
                        "name": event.get("name", ""),
                        "event_time": self.parse_event_time(event["event_time"]),
                        "status": event.get("status", "open"),
                        "location": location,
                    }
                )

                if created:
                    self.stdout.write(self.style.SUCCESS(f"Создано новое мероприятие: {obj.name} (ID: {obj.id})"))
                else:
                    self.stdout.write(self.style.WARNING(f"Обновлено мероприятие: {obj.name} (ID: {obj.id})"))

                stats['new' if created else 'updated'] += 1

            except Exception as e:
                self.stderr.write(self.style.ERROR(f"Ошибка при обработке события {event.get('id')}: {e}"))

        return stats

    def parse_event_time(self, time_str):
        return (datetime.fromisoformat(time_str) if time_str.endswith("Z")
                else timezone.localtime(datetime.fromisoformat(time_str)))