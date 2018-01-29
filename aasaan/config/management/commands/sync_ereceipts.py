# -*- coding: utf-8 -*-

import json
from datetime import date
from functools import partial

from django.core.management.base import BaseCommand

from schedulemaster.models import ProgramSchedule, ProgramScheduleCounts, \
 ProgramCountMaster, ProgramMaster

from config.ereceipts.ereceipts import EReceiptsInterface
from config.models import get_configuration

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from utils.datedeux import DateDeux


def get_receipts_collection(receipts_list, fields, tally_code_key, filter_tally_code=True):
    if not fields:
        return []

    if not tally_code_key:
        return []

    final_receipt_list = []        

    field_list = fields.split("\r\n")

    for receipt in receipts_list:
        if filter_tally_code:
            if tally_code_key not in receipt:
                continue

        current_receipt = dict()
        for field in field_list:
            if receipt.get(field):
                current_receipt[field] = receipt[field]

        final_receipt_list.append(current_receipt)

    return final_receipt_list


def get_program_master_abbreviations():
    return tuple((x.abbreviation for x in ProgramMaster.objects.all()))


def validate_tally_code(receipt, tally_code_key, abbreviations, splitter=" - "):
    _tally_code = receipt.get(tally_code_key, "")

    return _tally_code.split(splitter)[0] in abbreviations


def translate_receipt(receipt, tally_code_key, ereceipt_date_field="eReceiptDate"):
    """
        Remove tally_code_key and make receipt date ISO format
    """
    _dd = 0
    _mm = 1
    _yyyy = 2

    #receipt.pop(tally_code_key, None)

    _receipt_date_tuple = receipt[ereceipt_date_field].split("-")
    receipt[ereceipt_date_field] = "-".join([_receipt_date_tuple[_yyyy], _receipt_date_tuple[_mm],
                                            _receipt_date_tuple[_dd]])
    receipt["name"] = receipt.get("name", "").title()
    receipt["email"] = receipt.get("email", "").lower()

    return receipt


def update_schedule(receipt, tally_code_key, splitter=" - "):
    schedule_id = int(receipt[tally_code_key].split(splitter)[-1])

    try:
        schedule = ProgramSchedule.objects.get(id=schedule_id)
    except ObjectDoesNotExist:
        schedule = schedule_id
        print(receipt['eReceiptNumber'], schedule, "Not found")
        return 1

    schedule_receipts = json.loads(schedule.receipts) if schedule.receipts else []

    schedule_receipt_numbers = [x['eReceiptNumber'] for x in schedule_receipts]

    if receipt['eReceiptNumber'] in schedule_receipt_numbers:
        print(receipt['eReceiptNumber'], schedule, "Present")
        return 2

    receipt.pop(tally_code_key, None)
    schedule_receipts.append(receipt)

    schedule.receipts = json.dumps(schedule_receipts)
    schedule.save()

    print(receipt['eReceiptNumber'], schedule, "Updated")
    return 3


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
        program_master_abbreviations = get_program_master_abbreviations()
        _validator = partial(validate_tally_code, tally_code_key=tally_code_key, 
                            abbreviations=program_master_abbreviations)
        _translator = partial(translate_receipt, tally_code_key=tally_code_key)
        _updator = partial(update_schedule, tally_code_key=tally_code_key)                          

        for each_collection, each_report in [x.split("|") for x in get_configuration("SYNC_ERECEIPTS_COLLECTIONS").split("\r\n")]:
            receipts_list = ereceipts.get_receipts(start_date, end_date, each_collection, each_report)
            receipts_list_parsed = get_receipts_collection(receipts_list, field_list, tally_code_key)
            final_receipts_list = tuple(map(_translator, filter(_validator, receipts_list_parsed)))
            print(final_receipts_list)
            
            for receipt in final_receipts_list:
                #print(receipt)
                _result = _updator(receipt)