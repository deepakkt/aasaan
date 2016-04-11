# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-04-11 09:22
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('schedulemaster', '0008_auto_20160327_1455'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProgramAdditionalInformation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=50, verbose_name='title')),
                ('value', models.TextField(verbose_name='information')),
            ],
            options={
                'verbose_name': 'additional program information. (Do not use if not required)',
            },
        ),
        migrations.CreateModel(
            name='ProgramAdditionalLanguages',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('language', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='schedulemaster.LanguageMaster')),
            ],
        ),
        migrations.RenameField(
            model_name='programschedule',
            old_name='language',
            new_name='primary_language',
        ),
        migrations.RemoveField(
            model_name='programschedule',
            name='second_language',
        ),
        migrations.AddField(
            model_name='programschedule',
            name='event_management_software',
            field=models.CharField(blank=True, max_length=15),
        ),
        migrations.AddField(
            model_name='programschedule',
            name='gender',
            field=models.CharField(choices=[('BO', 'All Genders'), ('M', 'Gents'), ('F', 'Ladies')], default='BO', max_length=2),
        ),
        migrations.AlterField(
            model_name='programteacher',
            name='teacher_type',
            field=models.CharField(blank=True, choices=[('MT', 'Main Teacher'), ('CT', 'Co-Teacher'), ('OT', 'Observation Teacher'), ('O', 'Other')], default='MT', max_length=2, null=True),
        ),
        migrations.AddField(
            model_name='programadditionallanguages',
            name='program',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='schedulemaster.ProgramSchedule'),
        ),
        migrations.AddField(
            model_name='programadditionalinformation',
            name='program',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='schedulemaster.ProgramSchedule'),
        ),
    ]
