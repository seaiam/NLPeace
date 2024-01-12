# Generated by Django 4.2.5 on 2024-01-10 00:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0003_message_is_file_download_message_is_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='message',
            name='is_video',
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name='VideoUpload',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('video', models.FileField(upload_to='messageVideos')),
                ('message', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='chat.message')),
            ],
        ),
    ]
