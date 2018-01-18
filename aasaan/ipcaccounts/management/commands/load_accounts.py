# -*- coding: utf-8 -*-

"""
Sync schedules to google sheet
All definitions are given in gsync.settings
"""

import csv
from collections import Counter
from ipcaccounts.models import AccountsMaster, CourierDetails, TransactionNotes, VoucherMaster, EntityMaster, VoucherStatusMaster, VoucherDetails, ClassExpensesTypeMaster, TeacherExpensesTypeMaster
from datetime import date
from contacts.models import Zone, Center
from schedulemaster.models import ProgramSchedule
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

        row_headers = "TrackingNo,zone,account_type,Entity,VoucherDate,NatureoftheVoucher,programcode,BudgetCode,ExpensesDescription,PartyName,Amount,Details,CourieredDate,IPCNPRecived,DateofSubmissionFinance,MovementSheetno,Issues,PaymentDate,UTR,VoucherStatus,Remarks".split(",")

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
            key = current_row['Entity'] + current_row['VoucherDate'] + current_row['BudgetCode']
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
            # voucher_data['NameoftheCenter'] = current_row['NameoftheCenter']
            voucher_data['BudgetCode'] = current_row['BudgetCode']
            voucher_data['programcode'] = current_row['programcode']
            voucher_data['ExpensesDescription'] = current_row['ExpensesDescription']
            voucher_data['PartyName'] = current_row['PartyName']
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
            __base[key].append(voucher_data)
        for key, value in __base.items():
            ac_type = value[0]['account_type']
            accounts = AccountsMaster()
            accounts.account_type = ac_type
            # accounts.zone = Zone.objects.get(pk=value[0]['zone'])
            # filterargs = {'center_name': value[0]['NameoftheCenter'], 'zone': accounts.zone,}
            # accounts.center = Center.objects.get(**filterargs)
            accounts.entity_name = emk[value[0]['Entity']]
            accounts.budget_code = value[0]['BudgetCode']
            self.stdout.write('TrackingNo: %s' % value[0]['TrackingNo'])
            self.stdout.write('programcode: %s' % value[0]['programcode'])
            if ac_type == 'CA':
                accounts.program_schedule = ProgramSchedule.objects.get(pk=value[0]['programcode'])
            accounts.status = 'CL'
            accounts.save()
            counts['accounts_master'] += 1
            for each_voucher in value:
                counts['voucher'] += 1

                self.stdout.write('TrackingNo: %s' % each_voucher['TrackingNo'])
                self.stdout.write('Entity: %s' % each_voucher['Entity'])
                self.stdout.write('NatureoftheVoucher: %s' % each_voucher['NatureoftheVoucher'])
                # self.stdout.write('NameoftheCenter: %s' % each_voucher['NameoftheCenter'])
                self.stdout.write('BudgetCode: %s' % each_voucher['BudgetCode'])
                self.stdout.write('ExpensesDescription: %s' % each_voucher['ExpensesDescription'])
                self.stdout.write('PartyName: %s' % each_voucher['PartyName'])
                self.stdout.write('Amount: %s' % each_voucher['Amount'])
                # self.stdout.write('PhysicalMailapproval: %s' % each_voucher['PhysicalMailapproval'])

                self.stdout.write('Details: %s' % each_voucher['Details'])
                self.stdout.write('CourieredDate: %s' % each_voucher['CourieredDate'])
                self.stdout.write('IPCNPRecived: %s' % each_voucher['IPCNPRecived'])
                self.stdout.write('DateofSubmissionFinance: %s' % each_voucher['DateofSubmissionFinance'])
                self.stdout.write('MovementSheetno: %s' % each_voucher['MovementSheetno'])

                self.stdout.write('Issues: %s' % each_voucher['Issues'])
                self.stdout.write('PaymentDate: %s' % each_voucher['PaymentDate'])
                self.stdout.write('UTR: %s' % each_voucher['UTR'])
                self.stdout.write('VoucherStatus: %s' % each_voucher['VoucherStatus'])

                voucher = VoucherDetails()
                voucher.accounts_master = accounts
                voucher.tracking_no = each_voucher['TrackingNo']
                voucher.nature_of_voucher = vmk[each_voucher['NatureoftheVoucher']]
                voucher.voucher_status = vs[each_voucher['VoucherStatus']]
                dd,mm,yyyy = each_voucher['VoucherDate'].split('.')
                voucher.voucher_date = yyyy+'-'+mm+'-'+dd
                voucher.expenses_description = each_voucher['ExpensesDescription']
                voucher.party_name = each_voucher['PartyName']
                voucher.amount = each_voucher['Amount']
                voucher.save()


            # courier = CourierDetails()
            # note = TransactionNotes()

        self.stdout.write('Accounts => %d' % counts['accounts_master'])
        self.stdout.write('voucher => %d' % counts['voucher'])

