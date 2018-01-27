# -*- coding: utf-8 -*-

"""
Create ORS programs for newly defined programs in Aasaan
"""
from datetime import date
import json
from collections import Counter

from django.core.management.base import BaseCommand

from schedulemaster.models import ProgramSchedule, ProgramScheduleCounts, \
 ProgramCountMaster, ProgramReceiptAmounts
from config.ors.ors import ORSInterface
from config.models import get_configuration
from django.conf import settings

from utils.datedeux import DateDeux


def _return_category(category_name, category_set):
    for each_category in category_set:
        if each_category.category.count_category == category_name:
            return each_category

    return None


def _create_or_update(fields, values, schedule):
    _counts, _amounts = values
    categories = schedule.programreceiptamounts_set.all()

    for field in fields:
        _base_cat = ProgramCountMaster.objects.get(count_category=field)
        _model_cat = _return_category(field, categories) or ProgramReceiptAmounts()

        _model_cat.program = schedule
        _model_cat.category = _base_cat
        _model_cat.receipt_count = _counts[field]
        _model_cat.receipt_amount = _amounts[field]

        _model_cat.save()



class Command(BaseCommand):
    help = "Sync ereceipts amounts"

    def add_arguments(self, parser):
        parser.add_argument('start_date', nargs='?', type=str)


    def handle(self, *args, **options):
        _fields_to_update = ["Online Receipts", "Cash Receipts", "Cheque Receipts", "Creditcard Receipts"]

        if options['start_date']:
            _start_date = DateDeux.fromisodate(options['start_date'])
            print('Using start date of ', _start_date)
            _schedules = ProgramSchedule.objects.filter(start_date__gte=_start_date)
        else:
            reference_date = DateDeux.today() - 50
            print('Using start date of ', reference_date)
            _schedules = ProgramSchedule.objects.filter(start_date__gte=reference_date)

        for each_schedule in _schedules:
            _counts = Counter()
            _amounts = Counter()
            
            print(each_schedule.id, each_schedule)
            
            try:
                _receipts = json.loads(each_schedule.receipts)
            except:
                _receipts = []

            if not _receipts:
                print("No receipts found")
                continue

            for receipt in _receipts:
                _mode = receipt.get("mode", "Unknown")
                _mode = _mode.title() + " Receipts"
                _amount = receipt.get("amount", 0)

                _counts[_mode] += 1
                _amounts[_mode] += _amount

            print(_counts, _amounts)

            _create_or_update(_fields_to_update, (_counts, _amounts), 
                                each_schedule)


            
