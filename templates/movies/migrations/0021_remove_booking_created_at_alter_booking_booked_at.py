# Generated by Django 5.1.5 on 2025-02-19 16:05

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0020_movie_category'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='booking',
            name='created_at',
        ),
        migrations.AlterField(
            model_name='booking',
            name='booked_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
