# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-23 15:29
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('iconnect', '0005_auto_20160219_1553'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Mailer',
        ),
    ]
