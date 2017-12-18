# -*- coding: utf-8 -*-

"""
Sync schedules to google sheet
All definitions are given in gsync.settings
"""

import csv
from collections import Counter
from ipcaccounts.models import AccountsMaster, CourierDetails, TransactionNotes, VoucherMaster, EntityMaster, VoucherStatusMaster, VoucherDetails, ClassExpensesTypeMaster, TeacherExpensesTypeMaster
from contacts.models import Zone, Center, Contact
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError

class Command(BaseCommand):
    help = "Sync schedules. See gsync.settings for definitions"

    def add_arguments(self, parser):
        parser.add_argument('accounts_file', nargs='+', type=str)

    def handle(self, *args, **options):
        for each_file in options['accounts_file']:
            load_file = each_file
            break

        row_headers = "TrackingNo,zone,account_type,Entity,VoucherDate,NatureoftheVoucher,TeacherName,HeadOfExpenses,ExpensesDescription,Amount,Details,CourieredDate,IPCNPRecived,DateofSubmissionFinance,MovementSheetno,Issues,PaymentDate,UTR,VoucherStatus,Remarks".split(",")

        accounts_reader = csv.reader(open(load_file))

        counts = Counter()

        __base = {}

        em = EntityMaster.objects.all()
        emk = {}
        for m in em:
            emk[m.name] = m

        vm = VoucherMaster.objects.all()
        vmk = {}
        for m in vm:
            vmk[m.name] = m

        vsm = VoucherStatusMaster.objects.all()
        vs = {}
        for m in vsm:
            vs[m.name] = m

        for each_row in accounts_reader:
            if accounts_reader.line_num == 1:
                # bypass header row
                continue
            counts['processed'] += 1
            current_row = dict(zip(row_headers, each_row))
            key = current_row['Entity'] + current_row['VoucherDate'] + current_row['NatureoftheVoucher']
            try:
                __base[key]
            except KeyError:
                __base[key] = []
            voucher_data = {}
            voucher_data['TrackingNo'] = current_row['TrackingNo']
            voucher_data['zone'] = current_row['zone']
            voucher_data['account_type'] = current_row['account_type']
            voucher_data['Entity'] = current_row['Entity']
            voucher_data['VoucherDate'] = current_row['VoucherDate']
            voucher_data['NatureoftheVoucher'] = current_row['NatureoftheVoucher']
            voucher_data['TeacherName'] = current_row['TeacherName']
            voucher_data['HeadOfExpenses'] = current_row['HeadOfExpenses']
            voucher_data['ExpensesDescription'] = current_row['ExpensesDescription']
            voucher_data['Amount'] = current_row['Amount']
            voucher_data['Details'] = current_row['Details']
            voucher_data['CourieredDate'] = current_row['CourieredDate']
            voucher_data['IPCNPRecived'] = current_row['IPCNPRecived']
            voucher_data['DateofSubmissionFinance'] = current_row['DateofSubmissionFinance']
            voucher_data['MovementSheetno'] = current_row['MovementSheetno']
            voucher_data['Issues'] = current_row['Issues']
            voucher_data['PaymentDate'] = current_row['PaymentDate']
            voucher_data['UTR'] = current_row['UTR']
            voucher_data['VoucherStatus'] = current_row['VoucherStatus']
            voucher_data['Remarks'] = current_row['Remarks']
            __base[key].append(voucher_data)
        try:
            for key, value in __base.items():
                ac_type = value[0]['account_type']
                accounts = AccountsMaster()
                accounts.account_type = ac_type
                accounts.zone = Zone.objects.get(pk=value[0]['zone'])
                accounts.entity_name = emk[value[0]['Entity']]
                accounts.budget_code = value[0]['HeadOfExpenses']
                self.stdout.write('TrackingNo: %s' % value[0]['TrackingNo'])
                self.stdout.write('TeacherName: %s' % value[0]['TeacherName'])
                teacher_name = value[0]['TeacherName']
                accounts.teacher = Contact.objects.get(pk=teacher_name)
                accounts.status = 'CL'
                accounts.save()
                counts['accounts_master'] += 1
                for each_voucher in value:
                    counts['voucher'] += 1
                    voucher = VoucherDetails()
                    voucher.accounts_master = accounts
                    voucher.tracking_no = each_voucher['TrackingNo']
                    voucher.nature_of_voucher = vmk[each_voucher['NatureoftheVoucher']]
                    voucher.voucher_status = vs[each_voucher['VoucherStatus']]
                    dd,mm,yyyy = each_voucher['VoucherDate'].split('.')
                    voucher.voucher_date = yyyy+'-'+str(mm).zfill(2)+'-'+str(dd).zfill(2)
                    voucher.expenses_description = each_voucher['ExpensesDescription']
                    voucher.amount = each_voucher['Amount']
                    voucher.save()
        except IntegrityError:
            pass
        self.stdout.write('Teachers Accounts => %d' % counts['accounts_master'])
        self.stdout.write('voucher => %d' % counts['voucher'])

