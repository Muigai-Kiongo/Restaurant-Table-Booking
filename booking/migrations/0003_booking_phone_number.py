# Generated by Django 5.1.1 on 2024-10-29 12:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0002_remove_table_meal_options_booking_meal_option_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='booking',
            name='phone_number',
            field=models.CharField(max_length=15, null=True),
        ),
    ]
