# Generated by Django 5.0.6 on 2024-07-09 15:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_hashtag'),
    ]

    operations = [
        migrations.AddField(
            model_name='toot',
            name='hashtags',
            field=models.ManyToManyField(blank=True, related_name='toots', to='main.hashtag'),
        ),
    ]
