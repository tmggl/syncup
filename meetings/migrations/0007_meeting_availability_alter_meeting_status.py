# Generated by Django 5.1.7 on 2025-03-25 01:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meetings', '0006_meeting_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='meeting',
            name='availability',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='meeting', to='meetings.expertavailability'),
        ),
        migrations.AlterField(
            model_name='meeting',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected'), ('cancelled', 'Cancelled')], default='pending', max_length=10),
        ),
    ]
