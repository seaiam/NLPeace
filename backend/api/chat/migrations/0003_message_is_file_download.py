# Generated by Django 4.2.5 on 2023-12-28 01:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0002_fileupload'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='is_file_download',
            field=models.BooleanField(default=False),
        ),
    ]
