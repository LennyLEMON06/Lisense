# Generated by Django 5.2.1 on 2025-06-04 06:11

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('licen', '0012_alter_legalentity_options_alter_network_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='address',
            name='network',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='addresses', to='licen.network', verbose_name='Юридическое лицо'),
        ),
    ]
