# Generated by Django 4.2.5 on 2023-12-28 04:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_postsave_postsave_saver_post_unique'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='messaging_is_private',
            field=models.BooleanField(default=True),
        ),
    ]
