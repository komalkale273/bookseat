# Generated by Django 5.1.5 on 2025-02-16 12:43

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("movies", "0016_alter_seat_theater"),
    ]

    operations = [
        migrations.AddField(
            model_name="seat",
            name="is_reserved",
            field=models.BooleanField(default=False),
        ),
    ]
