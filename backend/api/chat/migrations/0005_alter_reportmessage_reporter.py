# Generated by Django 4.2.5 on 2024-01-09 00:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('chat', '0004_reportmessage'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reportmessage',
            name='reporter',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='message_reporter', to=settings.AUTH_USER_MODEL),
        ),
    ]
