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


        for each_collection, each_report in [x.split("|") for x in get_configuration("SYNC_ERECEIPTS_COLLECTIONS").split("\r\n")]:
            receipts_list = ereceipts.get_receipts(start_date, end_date, each_collection, each_report)
            #print(receipts_list)
            #print("%d receipts!" % len(receipts_list))
            print(json.dumps(receipts_list))