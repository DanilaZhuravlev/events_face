# Generated by Django 5.1.7 on 2025-03-19 14:15

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="SyncHistory",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "date",
                    models.DateTimeField(
                        auto_now_add=True, verbose_name="Дата синхронизации"
                    ),
                ),
                (
                    "new_events_count",
                    models.PositiveIntegerField(
                        default=0, verbose_name="Новых мероприятий"
                    ),
                ),
                (
                    "updated_events_count",
                    models.PositiveIntegerField(
                        default=0, verbose_name="Обновленных мероприятий"
                    ),
                ),
            ],
            options={
                "verbose_name": "История синхронизации",
                "verbose_name_plural": "История синхронизаций",
                "ordering": ["-date"],
            },
        ),
    ]
