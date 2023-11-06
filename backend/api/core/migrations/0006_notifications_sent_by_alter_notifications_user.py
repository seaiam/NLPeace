# Generated by Django 4.2.5 on 2023-11-06 01:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0005_alter_notifications_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='notifications',
            name='sent_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sent_by', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='notifications',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user', to=settings.AUTH_USER_MODEL),
        ),
    ]
