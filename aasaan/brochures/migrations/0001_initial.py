# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-06-17 14:55
from __future__ import unicode_literals

import brochures.models
from django.db import migrations, models
import django.db.models.deletion
import django_markdown.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contacts', '0019_auto_20160424_1149'),
        ('schedulemaster', '0014_programmaster_admin'),
    ]

    operations = [
        migrations.CreateModel(
            name='BrochureMaster',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('version', models.CharField(blank=True, max_length=10)),
                ('active', models.BooleanField(default=True)),
                ('brochure_image', models.ImageField(blank=True, upload_to=brochures.models._brochure_image_path)),
                ('description', django_markdown.models.MarkdownField(blank=True)),
                ('language', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='schedulemaster.LanguageMaster')),
            ],
            options={
                'verbose_name': 'Brochure Master',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Brochures',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.SmallIntegerField()),
                ('remarks', models.CharField(blank=True, max_length=100)),
                ('status', models.CharField(blank=True, choices=[('ACTV', 'Active'), ('DMGD', 'Damaged'), ('LOST', 'Lost')], default='ACTV', max_length=6)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='brochures.BrochureMaster')),
            ],
            options={
                'verbose_name': 'brochure',
                'verbose_name_plural': 'brochures',
            },
        ),
        migrations.CreateModel(
            name='BrochureSet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('remarks', models.CharField(blank=True, max_length=100)),
                ('program', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='schedulemaster.ProgramMaster')),
            ],
            options={
                'verbose_name': 'Brochure Set',
                'verbose_name_plural': 'Brochure Sets',
            },
        ),
        migrations.CreateModel(
            name='BrochureSetItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.SmallIntegerField()),
                ('brochure_set', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='brochures.BrochureSet')),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='brochures.BrochureMaster')),
            ],
        ),
        migrations.CreateModel(
            name='BrochuresShipment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sent_from', models.CharField(blank=True, max_length=50)),
                ('sent_to', models.CharField(blank=True, max_length=50)),
                ('sent_date', models.DateField(blank=True)),
                ('received_date', models.DateField(blank=True)),
                ('courier_vendor', models.CharField(blank=True, max_length=50)),
                ('courier_no', models.CharField(blank=True, max_length=50)),
                ('courier_status', models.CharField(blank=True, choices=[('CS', 'Courier Sent'), ('NEW', 'Not Initiated'), ('CR', 'Received'), ('IT', 'In Transit')], default='NEW', max_length=3)),
                ('remarks', models.CharField(blank=True, max_length=100)),
            ],
            options={
                'verbose_name': 'Brochure Shipment',
                'ordering': ['sent_date'],
            },
        ),
        migrations.CreateModel(
            name='BrochuresTransaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transfer_type', models.CharField(blank=True, choices=[('PSP', 'Printer to Stock Point'), ('SPSH', 'Stock Point to Schedule'), ('SCSP', 'Schedule to Stock Point'), ('STPT', 'Stock Point to Stock Point'), ('GUST', 'Stock Point to Guest')], default='STPT', max_length=6)),
                ('status', models.CharField(blank=True, choices=[('NEW', 'Transfer Initiated'), ('IT', 'In Transit'), ('DD', 'Delivered'), ('TC', 'Cancelled'), ('LOST', 'Lost/Damaged')], default='NEW', max_length=6)),
                ('source_printer', models.CharField(blank=True, max_length=100, null=True)),
                ('guest_name', models.CharField(blank=True, max_length=100, null=True)),
                ('guest_phone', models.CharField(blank=True, max_length=15, null=True)),
                ('guest_email', models.EmailField(blank=True, max_length=50, null=True)),
                ('transaction_status', models.CharField(blank=True, default='NEW', max_length=15, null=True)),
                ('transaction_date', models.DateField(auto_now_add=True)),
                ('brochure_set', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='brochures.BrochureSet')),
                ('destination_program_schedule', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='destination_sch', to='schedulemaster.ProgramSchedule')),
            ],
        ),
        migrations.CreateModel(
            name='BrochuresTransactionItem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sent_quantity', models.SmallIntegerField()),
                ('received_quantity', models.SmallIntegerField(blank=True, null=True)),
                ('brochures', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='brochures.BrochureMaster')),
                ('brochures_transfer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='brochures.BrochuresTransaction')),
            ],
        ),
        migrations.CreateModel(
            name='BroucherTransferNote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('note', django_markdown.models.MarkdownField()),
                ('note_timestamp', models.DateTimeField(auto_now_add=True)),
                ('brochure_transfer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='brochures.BrochuresTransaction')),
            ],
            options={
                'verbose_name': 'brochure transfer note',
                'ordering': ['-note_timestamp'],
                'verbose_name_plural': 'notes about brochure transfer',
            },
        ),
        migrations.CreateModel(
            name='StockPointAddress',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address_line_1', models.CharField(blank=True, max_length=100)),
                ('address_line_2', models.CharField(blank=True, max_length=100)),
                ('city', models.CharField(blank=True, max_length=50)),
                ('postal_code', models.CharField(blank=True, max_length=10)),
                ('state', models.CharField(blank=True, max_length=25)),
                ('country', models.CharField(blank=True, max_length=25)),
                ('contact_number1', models.CharField(blank=True, max_length=15, verbose_name='contact Number1')),
                ('contact_number2', models.CharField(blank=True, max_length=15, verbose_name='contact Number2')),
            ],
        ),
        migrations.CreateModel(
            name='StockPointMaster',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('active', models.BooleanField(default=True)),
                ('description', django_markdown.models.MarkdownField(blank=True)),
                ('zone', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contacts.Zone')),
            ],
            options={
                'verbose_name': 'Stock Point Master',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='StockPointNote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('note', django_markdown.models.MarkdownField()),
                ('note_timestamp', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Stock Point & Materials note',
                'ordering': ['-note_timestamp'],
                'verbose_name_plural': 'notes about Stock Point & Materials',
            },
        ),
        migrations.AddField(
            model_name='stockpointaddress',
            name='stock_point',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='brochures.StockPointMaster'),
        ),
        migrations.AddField(
            model_name='brochurestransaction',
            name='destination_stock_point',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='destination_sp', to='brochures.StockPointMaster'),
        ),
        migrations.AddField(
            model_name='brochurestransaction',
            name='source_program_schedule',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='schedulemaster.ProgramSchedule'),
        ),
        migrations.AddField(
            model_name='brochurestransaction',
            name='source_stock_point',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='brochures.StockPointMaster'),
        ),
        migrations.AddField(
            model_name='brochuresshipment',
            name='brochures_transfer',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='brochures.BrochuresTransaction'),
        ),
        migrations.AddField(
            model_name='brochures',
            name='stock_point',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='brochures.StockPointMaster'),
        ),
        migrations.CreateModel(
            name='StockPoint',
            fields=[
            ],
            options={
                'proxy': True,
                'verbose_name': 'Materials in Stock Point',
            },
            bases=('brochures.stockpointmaster',),
        ),
        migrations.AddField(
            model_name='stockpointnote',
            name='stock_point',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='brochures.StockPoint'),
        ),
        migrations.AlterUniqueTogether(
            name='brochuremaster',
            unique_together=set([('name', 'version', 'language')]),
        ),
    ]
