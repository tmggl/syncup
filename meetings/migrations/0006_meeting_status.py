# Generated by Django 5.1.7 on 2025-03-25 00:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meetings', '0005_alter_expertavailability_end_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='meeting',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved')], default='pending', max_length=10),
        ),
    ]
