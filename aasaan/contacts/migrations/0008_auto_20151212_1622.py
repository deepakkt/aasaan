# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2015-12-12 10:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0007_auto_20151208_2124'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='individualcontactrolecenter',
            options={'ordering': ['contact', 'role', 'center'], 'verbose_name': 'PCC center level contact role'},
        ),
        migrations.AlterModelOptions(
            name='individualcontactrolesector',
            options={'ordering': ['contact', 'role', 'sector'], 'verbose_name': 'PCC sector level contact role'},
        ),
        migrations.AlterModelOptions(
            name='individualcontactrolezone',
            options={'ordering': ['contact', 'role', 'zone'], 'verbose_name': 'PCC zone level contact role'},
        ),
        migrations.AlterModelOptions(
            name='individualrole',
            options={'ordering': ['role_name', 'role_level'], 'verbose_name': 'PCC Role'},
        ),
        migrations.AlterField(
            model_name='contact',
            name='id_card_number',
            field=models.CharField(blank=True, max_length=20, verbose_name='Ashram ID Card Number'),
        ),
        migrations.AlterField(
            model_name='contact',
            name='id_card_type',
            field=models.CharField(blank=True, max_length=10, verbose_name='Ashram ID Card Type'),
        ),
        migrations.AlterField(
            model_name='contact',
            name='id_proof_number',
            field=models.CharField(blank=True, max_length=30, verbose_name='govt ID Card Number'),
        ),
        migrations.AlterField(
            model_name='contact',
            name='id_proof_other',
            field=models.CharField(blank=True, max_length=30, verbose_name='type of govt ID if other'),
        ),
        migrations.AlterField(
            model_name='contact',
            name='id_proof_type',
            field=models.CharField(blank=True, choices=[('DL', 'Driving License'), ('PP', 'Passport'), ('RC', 'Ration Card'), ('VC', 'Voters ID'), ('AA', 'Aadhaar'), ('PC', 'PAN Card'), ('OT', 'Other Government Issued')], max_length=2, verbose_name='govt ID Proof Type'),
        ),
    ]
