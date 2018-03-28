# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2018-03-27 10:40
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion
import smart_selects.db_fields


class Migration(migrations.Migration):

    dependencies = [
        ('ipcaccounts', '0004_voucherdetails_voucher_type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='rcoaccountsmaster',
            name='status',
        ),
        migrations.RemoveField(
            model_name='voucherdetails',
            name='address1',
        ),
        migrations.RemoveField(
            model_name='voucherdetails',
            name='address2',
        ),
        migrations.RemoveField(
            model_name='voucherdetails',
            name='amount_after_tds',
        ),
        migrations.RemoveField(
            model_name='voucherdetails',
            name='approval_sent_date',
        ),
        migrations.RemoveField(
            model_name='voucherdetails',
            name='approved_date',
        ),
        migrations.RemoveField(
            model_name='voucherdetails',
            name='cheque',
        ),
        migrations.RemoveField(
            model_name='voucherdetails',
            name='finance_submission_date',
        ),
        migrations.RemoveField(
            model_name='voucherdetails',
            name='movement_sheet_no',
        ),
        migrations.RemoveField(
            model_name='voucherdetails',
            name='np_voucher_status',
        ),
        migrations.RemoveField(
            model_name='voucherdetails',
            name='voucher_date',
        ),
        migrations.RemoveField(
            model_name='voucherdetails',
            name='voucher_status',
        ),
        migrations.AddField(
            model_name='rcoaccountsmaster',
            name='approval_sent_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='rcoaccountsmaster',
            name='approved_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='rcoaccountsmaster',
            name='finance_submission_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='rcoaccountsmaster',
            name='movement_sheet_no',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='rcoaccountsmaster',
            name='np_voucher_status',
            field=smart_selects.db_fields.GroupedForeignKey(blank=True, group_field='type', null=True, on_delete=django.db.models.deletion.CASCADE, to='ipcaccounts.NPVoucherStatusMaster'),
        ),
        migrations.AddField(
            model_name='rcoaccountsmaster',
            name='rco_voucher_status',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='ipcaccounts.RCOVoucherStatusMaster'),
        ),
        migrations.AddField(
            model_name='rcoaccountsmaster',
            name='voucher_date',
            field=models.DateField(default=datetime.date.today, verbose_name='Voucher Date'),
        ),
        migrations.AddField(
            model_name='voucherdetails',
            name='tds_amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name='TDS Amount'),
        ),
    ]
