# Generated by Django 5.0.6 on 2024-07-09 15:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_toot_hashtags'),
    ]

    operations = [
        migrations.AddField(
            model_name='hashtag',
            name='slug',
            field=models.SlugField(default='', editable=False, verbose_name='スラッグ'),
        ),
    ]