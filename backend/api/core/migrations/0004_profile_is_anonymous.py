# Generated by Django 4.2.5 on 2024-03-29 21:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_temporaryaccount'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='is_anonymous',
            field=models.BooleanField(default=False),
        ),
    ]
