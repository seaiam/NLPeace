# Generated by Django 4.2.5 on 2024-01-12 00:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0008_rename_reported_reportmessage_reporter'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='gif_url',
            field=models.URLField(blank=True, null=True),
        ),
    ]