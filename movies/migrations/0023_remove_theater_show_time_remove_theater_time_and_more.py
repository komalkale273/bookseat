# Generated by Django 5.1.5 on 2025-02-19 16:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0022_remove_booking_total_price_alter_booking_amount_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='theater',
            name='show_time',
        ),
        migrations.RemoveField(
            model_name='theater',
            name='time',
        ),
        migrations.RemoveField(
            model_name='theater',
            name='total_seats',
        ),
        migrations.AddField(
            model_name='theater',
            name='base_price',
            field=models.DecimalField(decimal_places=2, default=100.0, max_digits=6),
        ),
        migrations.AddField(
            model_name='theater',
            name='capacity',
            field=models.IntegerField(default=100),
        ),
        migrations.AddField(
            model_name='theater',
            name='location',
            field=models.CharField(default='Unknown Location', max_length=255),
        ),
    ]
