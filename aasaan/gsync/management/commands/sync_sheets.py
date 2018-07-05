# -*- coding: utf-8 -*-

"""
Sync schedules to google sheet
All definitions are given in gsync.settings
"""

import json
from os.path import join as path_join

from django.core.management.base import BaseCommand
from django.conf import settings

from schedulemaster.models import ProgramSchedule, ProgramScheduleCounts
from utils.datedeux import DateDeux
from utils.dict_helpers import *


def date_translate(pydate):
    _date = DateDeux.frompydate(pydate)
    return _date.dateformat('dd-mmm-yyyy')


def date_get_age(pyts):
    _date = pyts.date()

    try:
        return DateDeux.today() - _date
    except:
        return 99


def status_translate(status):
    if status == "RO":
        return "Registration Open"
    elif status == "CA":
        return "Cancelled"
    elif status == "RC":
        return "Registration Closed"
    else:
        return status


def get_schedules():
    schedules = ProgramSchedule.objects.filter(start_date__gte=(DateDeux.today()-60)).filter(hidden=False).filter(program__admin=False).order_by('center__zone__zone_name', '-start_date').values('center__zone__zone_name', 'start_date', 'end_date', 'center__center_name', 'program__name', 'gender', 'primary_language__name', 'status', 'event_management_code', 'online_registration_code', 'contact_phone1', 'contact_email', 'created', 'id')

    schedules = list(schedules)
    schedules = translate_values(schedules, 'start_date', date_translate)
    schedules = translate_values(schedules, 'end_date', date_translate)
    schedules = translate_values(schedules, 'status', status_translate)
    schedules = translate_values(schedules, 'created', date_get_age)

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
    return schedules


def get_enrollments(schedules):
    enrollments = []
    _base_cols = ('ORS Address List Count',
    'ORS Absent Count',
    'Joomla Paid Count',
    'ORS Participant Count',
    'ORS VIFO Count',
    'ORS Online Count')       

    for each_schedule in schedules:
        _counts = list(ProgramScheduleCounts.objects.filter(program_id=each_schedule['id']).values('category__count_category', 'value'))

        _heading = pluck(_counts, 'category__count_category')
        _value = pluck(_counts, 'value')

        count_map = dict(zip(_heading, _value))
        count_map = normalize([count_map], _base_cols, "")[0]

        enrollments.append(merge_dicts(each_schedule, count_map))  

    return enrollments  


class Command(BaseCommand):
    help = "Sync schedules. See gsync.settings for definitions"

    def handle(self, *args, **options):
        # use this for test
        #output_path = "/tmp"

        # use this for prod
        output_path = path_join(settings.MEDIA_ROOT, "schedules")

        schedule_output_file = path_join(output_path, "schedules.json")
        enrollment_output_file = path_join(output_path, "enrollments.json")

        schedules = get_schedules()
        enrollments = get_enrollments(schedules)

        schedules_json = json.dumps(schedules, indent=4, sort_keys=True)
        enrollments_json = json.dumps(enrollments, indent=4, sort_keys=True)

        f = open(schedule_output_file, "w")
        f.write(schedules_json)
        f.close()

        f = open(enrollment_output_file, "w")
        f.write(enrollments_json)
        f.close()

        print("JSONs ==>  ", schedule_output_file, enrollment_output_file)