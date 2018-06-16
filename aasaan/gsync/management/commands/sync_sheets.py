# -*- coding: utf-8 -*-

"""
Sync schedules to google sheet
All definitions are given in gsync.settings
"""

import json

from django.core.management.base import BaseCommand
from schedulemaster.models import ProgramSchedule
from utils.datedeux import DateDeux
from utils.dict_helpers import *


def date_translate(pydate):
    from utils.datedeux import DateDeux
    _date = DateDeux.frompydate(pydate)
    return _date.dateformat('dd-mmm-yyyy')


def status_translate(status):
    if status == "RO":
        return "Registration Open"
    elif status == "CA":
        return "Cancelled"
    elif status == "RC":
        return "Registration Closed"
    else:
        return status


class Command(BaseCommand):
    help = "Sync schedules. See gsync.settings for definitions"

    def handle(self, *args, **options):
        output_file = "/var/www/aasaan/media/schedules/schedule.json"
        #output_file = "/tmp/schedule.json"

        schedules = ProgramSchedule.objects.filter(start_date__gte=(DateDeux.today()-60)).filter(hidden=False).filter(program__admin=False).order_by('center__zone__zone_name', '-start_date').values('center__zone__zone_name', 'start_date', 'end_date', 'center__center_name', 'program__name', 'gender', 'primary_language__name', 'status', 'event_management_code', 'online_registration_code', 'contact_phone1', 'contact_email', 'id')

        schedules = list(schedules)
        schedules = translate_values(schedules, 'start_date', date_translate)
        schedules = translate_values(schedules, 'end_date', date_translate)
        schedules = translate_values(schedules, 'status', status_translate)

        kex = (
            ('center__zone__zone_name', 'Zone Name'),
            ('start_date', 'Program Start Date'),
            ('end_date', 'Program End Date'),
            ('center__center_name', 'Center Name'),
            ('program__name', 'Program Type'),
            ('gender', 'Gender'),
            ('primary_language__name', 'Language'),
            ('status', 'Status'),
            ('event_management_code', 'ORS Code'),
            ('online_registration_code', 'Joomla Code'),
            ('contact_phone1', 'Contact Phone'),
            ('contact_email', 'Contact Email')
        )        

        schedules = translate_keys(schedules, kex)
        schedules_json = json.dumps(schedules)

        f = open(output_file, "w")
        f.write(schedules_json)
        f.close()

        print("Written new json to ", output_file)