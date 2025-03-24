# Generated by Django 5.1.7 on 2025-03-23 10:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('meetings', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='meeting',
            name='platform',
            field=models.CharField(choices=[('zoom', 'Zoom'), ('meet', 'Google Meet')], default='zoom', max_length=10),
        ),
    ]
