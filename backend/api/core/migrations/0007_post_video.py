# Generated by Django 4.2.5 on 2024-01-10 01:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_post_is_edited'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='video',
            field=models.FileField(blank=True, null=True, upload_to='postVideos/'),
        ),
    ]
