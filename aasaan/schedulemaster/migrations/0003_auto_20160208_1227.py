# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-02-08 06:57
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('schedulemaster', '0002_auto_20160208_1209'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProgramCountMaster',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('count_category', models.CharField(max_length=100)),
                ('active', models.BooleanField(default=True)),
                ('notes', models.TextField(blank=True)),
            ],
            options={
                'ordering': ['count_category'],
                'verbose_name': 'program count type',
            },
        ),
        migrations.CreateModel(
            name='ProgramScheduleCounts',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('count', models.IntegerField(default=0)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='schedulemaster.ProgramCountMaster')),
                ('program', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='schedulemaster.ProgramSchedule')),
            ],
            options={
                'verbose_name': 'program counts',
            },
        ),
        migrations.RemoveField(
            model_name='programcounts',
            name='program',
        ),
        migrations.AlterModelOptions(
            name='programcategory',
            options={'ordering': ['name'], 'verbose_name': 'Program Category', 'verbose_name_plural': 'Program Categories'},
        ),
        migrations.AlterModelOptions(
            name='programschedulenote',
            options={'verbose_name': 'program note', 'verbose_name_plural': 'notes about program'},
        ),
        migrations.AlterField(
            model_name='programbatch',
            name='end_time',
            field=models.CharField(blank=True, max_length=10),
        ),
        migrations.DeleteModel(
            name='ProgramCounts',
        ),
    ]
