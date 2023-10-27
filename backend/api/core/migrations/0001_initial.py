# Generated by Django 4.2.5 on 2023-10-24 21:32
# Generated by Django 4.2.5 on 2023-10-18 21:26

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.RESTRICT, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('bio', models.TextField(blank=True, null=True)),
                ('banner', models.ImageField(blank=True, null=True, upload_to='profileBanners/')),
                ('pic', models.ImageField(blank=True, null=True, upload_to='profilePictures/')),
                ('forget_password_token', models.CharField(default='', max_length=100)),
                ('is_private', models.BooleanField(default=True)),
            ],
        ),
    ]
