# -*- coding: utf-8 -*-

import json
from datetime import date

from django.core.management.base import BaseCommand

from schedulemaster.models import ProgramSchedule, ProgramScheduleCounts, \
 ProgramCountMaster

from config.ereceipts.ereceipts import EReceiptsInterface
from config.models import get_configuration

from django.conf import settings

from utils.datedeux import DateDeux


def get_receipts_collection(receipts_list, fields, tally_code_key):
    if not fields:
        return []

    if not tally_code_key:
        return []

    final_receipt_list = []        

    field_list = fields.split("\r\n")

    for receipt in receipts_list:
        if tally_code_key not in receipt:
            continue

        current_receipt = dict()
        for field in field_list:
            if receipt.get(field):
                current_receipt[field] = receipt[field]

        final_receipt_list.append(current_receipt)

    return final_receipt_list


class Command(BaseCommand):
    help = "Set programs with past date as 'registration closed'"

    def add_arguments(self, parser):
        parser.add_argument('start_date', nargs='?', type=str)
        parser.add_argument('end_date', nargs='?', type=str)


    def handle(self, *args, **options):
        _fields_to_update = ["Joomla Paid Count"]
        ereceipts = EReceiptsInterface(settings.ERECEIPTS_USER, settings.ERECEIPTS_PASSWORD)
        ereceipts.authenticate()

        if options['start_date']:
            start_date = DateDeux.fromisodate(options['start_date'])
            end_date = DateDeux.fromisodate(options['end_date'])
        else:
            start_date = end_date = DateDeux.today() - 1

        print("Using dates %s and %s" % (start_date, end_date))

        field_list = get_configuration("SYNC_ERECEIPTS_FIELDS")
        tally_code_key = get_configuration("SYNC_ERECEIPTS_TALLYCODE_JSONSTRING")

        for each_collection, each_report in [x.split("|") for x in get_configuration("SYNC_ERECEIPTS_COLLECTIONS").split("\r\n")]:
            receipts_list = ereceipts.get_receipts(start_date, end_date, each_collection, each_report)
            receipts_list_parsed = get_receipts_collection(receipts_list, field_list, tally_code_key)
            print(receipts_list_parsed)