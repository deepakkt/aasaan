# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2018-04-08 09:58
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contacts', '0024_auto_20171224_1428'),
    ]

    operations = [
        migrations.CreateModel(
            name='Travellers',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('teacher', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='contacts.Contact')),
            ],
            options={
                'verbose_name': 'Traveller',
            },
        ),
        migrations.CreateModel(
            name='TravelRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('_from', models.CharField(blank=True, max_length=100)),
                ('_to', models.CharField(blank=True, max_length=100)),
                ('onward_date', models.DateField(blank=True, null=True, verbose_name='Date of Journey')),
                ('travel_mode', models.CharField(choices=[('TR', 'Train'), ('BS', 'Bus'), ('FL', 'Flight')], default='TR', max_length=2)),
                ('remarks', models.CharField(blank=True, max_length=200, null=True, verbose_name='Remarks')),
                ('status', models.CharField(choices=[('IP', 'In-Progress'), ('BK', 'Booked'), ('CL', 'Cancelled'), ('PD', 'Processed')], default='IP', max_length=2)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('zone', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='contacts.Zone', verbose_name='Zone')),
            ],
            options={
                'verbose_name': 'Travel Request',
                'ordering': ['onward_date'],
            },
        ),
        migrations.AddField(
            model_name='travellers',
            name='travel_request',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='travels.TravelRequest'),
        ),
    ]
