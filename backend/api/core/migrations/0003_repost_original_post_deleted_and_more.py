# Generated by Django 4.2.5 on 2023-11-04 23:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_repost'),
    ]

    operations = [
        migrations.AddField(
            model_name='repost',
            name='original_post_deleted',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='repost',
            name='original_post',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reposts', to='core.post'),
        ),
    ]