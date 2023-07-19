# Generated by Django 4.0.6 on 2022-07-18 17:19

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('post', '0015_merge_20220715_1654'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='likes',
            field=models.ManyToManyField(related_name='twitter_post', to=settings.AUTH_USER_MODEL),
        ),
    ]
