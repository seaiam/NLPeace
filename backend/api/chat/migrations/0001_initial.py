
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ChatRoom',
            fields=[
                ('room_name', models.AutoField(primary_key=True, serialize=False, unique=True)),
                ('initiated_by_user1', models.BooleanField(default=False)),
                ('initiated_by_user2', models.BooleanField(default=False)),
                ('user1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user1', to=settings.AUTH_USER_MODEL)),
                ('user2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user2', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('is_file_download', models.BooleanField(default=False)),
                ('is_image', models.BooleanField(default=False)),
                ('is_video', models.BooleanField(default=False)),
                ('gif_url', models.URLField(blank=True, null=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='author_messages', to=settings.AUTH_USER_MODEL)),
                ('room_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='room_id', to='chat.chatroom')),
            ],
        ),
        migrations.CreateModel(
            name='VideoUpload',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('video', models.FileField(upload_to='messageVideos')),
                ('message', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='chat.message')),
            ],
        ),
        migrations.CreateModel(
            name='ReportMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.IntegerField(choices=[(0, 'Hate'), (1, 'Abuse and harassment'), (2, 'Violent speech')], default=0)),
                ('message', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='chat.message')),
                ('reporter', models.ForeignKey(default=None, on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ImageUpload',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='messageImages')),
                ('message', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='chat.message')),
            ],
        ),
        migrations.CreateModel(
            name='FileUpload',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='messageFiles')),
                ('message', models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='chat.message')),
            ],
        ),
    ]
