# Generated by Django 4.2.5 on 2023-10-18 00:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_user_forget_password_token'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='forget_password_token',
        ),
    ]
