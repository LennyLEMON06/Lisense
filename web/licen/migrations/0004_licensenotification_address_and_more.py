# Generated by Django 5.2.1 on 2025-05-16 13:13

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('licen', '0003_computer_cryptopro_ecp_fiscalnumber_honestsign_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='licensenotification',
            name='address',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='license_notifications', to='licen.address', verbose_name='Адрес'),
        ),
        migrations.AddField(
            model_name='licensenotification',
            name='legal_entity',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='license_notifications', to='licen.legalentity', verbose_name='Юридическое лицо'),
        ),
        migrations.AlterField(
            model_name='licensenotification',
            name='computer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='license_notifications', to='licen.computer', verbose_name='Компьютер'),
        ),
    ]
