
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Advertisement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('advertiser', models.CharField(max_length=512)),
                ('logo', models.ImageField(blank=True, null=True, upload_to='adLogos/')),
                ('content', models.CharField(max_length=280)),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('content', models.CharField(max_length=280)),
                ('image', models.ImageField(blank=True, null=True, upload_to='postImages/')),
                ('video', models.FileField(blank=True, null=True, upload_to='postVideos/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_edited', models.BooleanField(default=False)),
                ('parent_post', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='replies', to='core.post')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.RESTRICT, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('bio', models.TextField(blank=True, null=True)),
                ('banner', models.ImageField(blank=True, null=True, upload_to='profileBanners/')),
                ('pic', models.ImageField(blank=True, null=True, upload_to='profilePictures/')),
                ('forget_password_token', models.CharField(default='', max_length=100)),
                ('is_private', models.BooleanField(default=True)),
                ('is_banned', models.BooleanField(default=False)),
                ('messaging_is_private', models.BooleanField(default=True)),
                ('blocked', models.ManyToManyField(blank=True, related_name='blocked', to=settings.AUTH_USER_MODEL)),
                ('follow_requests', models.ManyToManyField(blank=True, related_name='follow_requests', to=settings.AUTH_USER_MODEL)),
                ('followers', models.ManyToManyField(blank=True, related_name='followers', to=settings.AUTH_USER_MODEL)),
                ('following', models.ManyToManyField(blank=True, related_name='following', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.IntegerField(choices=[(0, 'Hate'), (1, 'Abuse and harassment'), (2, 'User is pretending to be someone else')])),
                ('info', models.TextField(blank=True, null=True)),
                ('date_reported', models.DateTimeField(auto_now_add=True)),
                ('reported', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reported', to=settings.AUTH_USER_MODEL)),
                ('reporter', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='reporter', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Repost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('post', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='reposts', to='core.post')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ProfileWarning',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('issued_at', models.DateTimeField(auto_now_add=True)),
                ('note', models.TextField(blank=True, null=True)),
                ('issuer', models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
                ('offender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='offender', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ProfileInterest',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.RESTRICT, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('bio', models.TextField(blank=True, null=True)),
                ('banner', models.ImageField(blank=True, null=True, upload_to='profileBanners/')),
                ('pic', models.ImageField(blank=True, null=True, upload_to='profilePictures/')),
                ('forget_password_token', models.CharField(default='', max_length=100)),
                ('is_private', models.BooleanField(default=True)),
                ('is_banned', models.BooleanField(default=False)),
                ('messaging_is_private', models.BooleanField(default=True)),
                ('blocked', models.ManyToManyField(blank=True, related_name='blocked', to=settings.AUTH_USER_MODEL)),
                ('follow_requests', models.ManyToManyField(blank=True, related_name='follow_requests', to=settings.AUTH_USER_MODEL)),
                ('followers', models.ManyToManyField(blank=True, related_name='followers', to=settings.AUTH_USER_MODEL)),
                ('following', models.ManyToManyField(blank=True, related_name='following', to=settings.AUTH_USER_MODEL)),
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=1024)),
                ('last_expressed', models.DateTimeField()),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.profile')),
            ],
        ),
        migrations.CreateModel(
            name='PostSave',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.post')),
                ('saver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PostReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.IntegerField(choices=[(0, 'Hate'), (1, 'Abuse and harassment'), (2, 'Violent speech')], default=2)),
                ('info', models.TextField(blank=True, null=True)),
                ('date_reported', models.DateTimeField(auto_now_add=True)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.post')),
                ('reporter', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PostPin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pinner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.post')),
            ],
        ),
        migrations.CreateModel(
            name='PostLike',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('liker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.post')),
            ],
        ),
        migrations.CreateModel(
            name='PostDislike',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('disliker', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.post')),
            ],
        ),
        migrations.CreateModel(
            name='Notifications',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('notifications', models.TextField()),
                ('type', models.CharField(blank=True, null=True)),
                ('sent_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sent_by', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='AdvertisementTopic',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=1024)),
                ('ad', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.advertisement')),
            ],
        ),
        migrations.AddConstraint(
            model_name='postsave',
            constraint=models.UniqueConstraint(fields=('saver', 'post'), name='saver_post_unique'),
        ),
        migrations.AddConstraint(
            model_name='postpin',
            constraint=models.UniqueConstraint(fields=('pinner', 'post'), name='pinner_post_unique'),
        ),
        migrations.AddConstraint(
            model_name='postlike',
            constraint=models.UniqueConstraint(fields=('liker', 'post'), name='liker_post_unique'),
        ),
        migrations.AddConstraint(
            model_name='postdislike',
            constraint=models.UniqueConstraint(fields=('disliker', 'post'), name='disliker_post_unique'),
        ),
    ]
