# Generated by Django 4.2.5 on 2023-12-26 10:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='gif',
            field=models.FileField(blank=True, null=True, upload_to='gifs/'),
        ),
    ]