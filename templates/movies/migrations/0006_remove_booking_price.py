# Generated by Django 5.1.5 on 2025-02-10 19:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0005_booking_price'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='booking',
            name='price',
        ),
    ]
