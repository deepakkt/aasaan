# -*- coding: utf-8 -*-

"""
Sync schedules to google sheet
All definitions are given in gsync.settings
"""

import json

from django.core.management.base import BaseCommand
from schedulemaster.models import ProgramSchedule, ProgramScheduleCounts
from utils.datedeux import DateDeux
from utils.dict_helpers import *

from .sync_sheets import get_schedules


class Command(BaseCommand):
    help = "While this works to sync enrollments, sync_sheets will now sync both schedules and enrollments. This should no longer be used."

    def handle(self, *args, **options):
        #output_file = "/var/www/aasaan/media/schedules/enrollments.json"
        output_file = "/tmp/enrollments.json"

        _base_cols = ('ORS Address List Count',
        'ORS Absent Count',
        'Joomla Paid Count',
        'ORS Participant Count',
        'ORS VIFO Count',
        'ORS Online Count')        

        schedules = get_schedules()



        schedules_json = json.dumps(enrollments, indent=4, sort_keys=True)

        f = open(output_file, "w")
        f.write(schedules_json)
        f.close()

        print("Written new json to ", output_file)