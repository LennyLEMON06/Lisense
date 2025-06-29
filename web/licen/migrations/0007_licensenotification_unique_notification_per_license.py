# Generated by Django 5.2.1 on 2025-05-22 15:08

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('licen', '0006_licensenotification_days_left'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='licensenotification',
            constraint=models.UniqueConstraint(fields=('license_type', 'license_id', 'notification_type'), name='unique_notification_per_license'),
        ),
    ]
