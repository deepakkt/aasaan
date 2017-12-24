# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2017-12-23 10:17
from __future__ import unicode_literals

from django.db import migrations
import django.db.models.deletion
import smart_selects.db_fields


class Migration(migrations.Migration):

    dependencies = [
        ('schedulemaster', '0027_auto_20171206_1518'),
    ]

    operations = [
        migrations.AlterField(
            model_name='programschedule',
            name='center',
            field=smart_selects.db_fields.GroupedForeignKey(group_field='zone', on_delete=django.db.models.deletion.CASCADE, to='contacts.Center'),
        ),
    ]
