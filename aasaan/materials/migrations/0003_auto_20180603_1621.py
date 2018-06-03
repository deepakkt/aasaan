# Generated by Django 2.0.4 on 2018-06-03 10:51

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('materials', '0002_auto_20180522_1408'),
    ]

    operations = [
        migrations.AddField(
            model_name='materialsrequest',
            name='notify_meta',
            field=django.contrib.postgres.fields.jsonb.JSONField(default='{}'),
        ),
        migrations.AddField(
            model_name='materialsrequest',
            name='notify_toggle',
            field=models.BooleanField(default=False),
        ),
    ]
