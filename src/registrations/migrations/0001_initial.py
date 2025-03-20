# Generated by Django 5.1.7 on 2025-03-20 10:03

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('events', '0002_event_registration_deadline'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Registration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('registration_time', models.DateTimeField(auto_now_add=True, verbose_name='Время регистрации')),
                ('status', models.CharField(choices=[('pending', 'В ожидании'), ('confirmed', 'Подтверждена'), ('rejected', 'Отклонена')], default='pending', max_length=20, verbose_name='Статус регистрации')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='registrations', to='events.event', verbose_name='Мероприятие')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='registrations', to=settings.AUTH_USER_MODEL, verbose_name='Посетитель')),
            ],
            options={
                'verbose_name': 'Регистрация',
                'verbose_name_plural': 'Регистрации',
                'ordering': ['-registration_time'],
                'unique_together': {('user', 'event')},
            },
        ),
    ]
