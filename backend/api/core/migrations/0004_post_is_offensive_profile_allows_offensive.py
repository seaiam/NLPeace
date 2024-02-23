# Generated by Django 4.2.5 on 2024-02-15 00:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_alter_hashtag_content'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='is_offensive',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='profile',
            name='allows_offensive',
            field=models.BooleanField(default=False),
        ),
    ]
