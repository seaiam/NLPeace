# Generated by Django 4.2.5 on 2024-01-06 19:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0002_imageupload_fileupload'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='is_file_download',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='message',
            name='is_image',
            field=models.BooleanField(default=False),
        ),
    ]