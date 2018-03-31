# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2018-03-31 07:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ipcaccounts', '0008_treasurer'),
    ]

    operations = [
        migrations.AddField(
            model_name='treasurer',
            name='request_type',
            field=models.CharField(choices=[('ADD', 'Add Treasurer'), ('CHG', 'Change Treasurer')], default='ADD', max_length=3),
        ),
    ]
