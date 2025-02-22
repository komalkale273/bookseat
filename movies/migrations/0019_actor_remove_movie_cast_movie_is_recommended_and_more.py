# Generated by Django 5.1.5 on 2025-02-17 17:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0018_alter_booking_movie_alter_booking_seat_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Actor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('bio', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='movie',
            name='cast',
        ),
        migrations.AddField(
            model_name='movie',
            name='is_recommended',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='movie',
            name='actors',
            field=models.ManyToManyField(blank=True, related_name='movies', to='movies.actor'),
        ),
    ]
