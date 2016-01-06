# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-01-06 11:07
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django_markdown.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contacts', '0009_auto_20160106_1637'),
    ]

    operations = [
        migrations.CreateModel(
            name='CenterItemNotes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('note', django_markdown.models.MarkdownField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('center', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contacts.Center')),
            ],
        ),
        migrations.CreateModel(
            name='CenterMaterial',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.SmallIntegerField()),
                ('status', models.CharField(blank=True, choices=[('ACTV', 'Active'), ('DMGD', 'Damaged'), ('LOST', 'Lost'), ('LOAN', 'Loaned')], default='ACTV', max_length=6)),
                ('center', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contacts.Center')),
            ],
        ),
        migrations.CreateModel(
            name='ItemMaster',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('model_no', models.CharField(blank=True, max_length=50)),
                ('description', django_markdown.models.MarkdownField()),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_type', models.CharField(blank=True, choices=[('IKDN', 'In-Kind Donation'), ('PURC', 'Cash Purchase'), ('LOAN', 'Loan'), ('LOCL', 'Loan Closure')], max_length=6)),
                ('transaction_date', models.DateField(auto_now_add=True)),
                ('description', django_markdown.models.MarkdownField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-transaction_date', 'transaction_type'],
            },
        ),
        migrations.CreateModel(
            name='TransactionItems',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.SmallIntegerField()),
                ('unit_cost', models.DecimalField(decimal_places=2, default=0, max_digits=9)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='materials.ItemMaster')),
            ],
        ),
        migrations.CreateModel(
            name='TransactionNotes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('note', django_markdown.models.MarkdownField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-created'],
            },
        ),
        migrations.CreateModel(
            name='DonationTransaction',
            fields=[
                ('transaction', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='materials.Transaction')),
                ('donor_first_name', models.CharField(max_length=50)),
                ('donor_last_name', models.CharField(blank=True, max_length=50)),
                ('donor_mobile', models.CharField(blank=True, max_length=15)),
                ('donor_email', models.EmailField(blank=True, max_length=50)),
                ('donated_date', models.DateField(auto_now_add=True)),
                ('donation_remarks', django_markdown.models.MarkdownField()),
            ],
        ),
        migrations.CreateModel(
            name='LoanTransaction',
            fields=[
                ('transaction', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='materials.Transaction')),
                ('loan_date', models.DateField(auto_now_add=True)),
                ('loan_status', models.CharField(blank=True, choices=[('LOND', 'Loaned'), ('LOCL', 'Loan Closed'), ('LOPR', 'Loan - Partially Returned'), ('LCPR', 'Loan Closed - Partially Returned')], max_length=6)),
                ('destination_center', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contacts.Center')),
            ],
        ),
        migrations.CreateModel(
            name='PurchaseTransaction',
            fields=[
                ('transaction', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='materials.Transaction')),
                ('invoice_number', models.CharField(max_length=50)),
                ('supplier_name', models.CharField(max_length=100)),
                ('bill_date', models.DateTimeField(auto_now_add=True)),
                ('bill_soft_copy', models.FileField(blank=True, upload_to='')),
                ('total_cost', models.DecimalField(decimal_places=2, default=0, max_digits=9)),
                ('payment_remarks', django_markdown.models.MarkdownField()),
            ],
        ),
        migrations.AddField(
            model_name='transactionnotes',
            name='transaction',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='materials.Transaction'),
        ),
        migrations.AddField(
            model_name='transactionitems',
            name='transaction',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='materials.Transaction'),
        ),
        migrations.AddField(
            model_name='transaction',
            name='center',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contacts.Center'),
        ),
        migrations.AddField(
            model_name='centermaterial',
            name='item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='materials.ItemMaster'),
        ),
    ]
