# Generated by Django 5.1.7 on 2025-03-20 08:24

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("events", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="event",
            name="registration_deadline",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
