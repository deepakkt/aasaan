# -*- coding: utf-8 -*-

"""
Sync schedules to google sheet
All definitions are given in gsync.settings
"""

import json
from os.path import join as path_join

from django.core.management.base import BaseCommand
from django.conf import settings
from django.db.models import Case, When, Value

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


def get_schedules(queryset=None):
    column_list = ['center__zone__zone_name', 'start_date', 'end_date', 
    'center__center_name', 'final_event_name', 'gender', 
    'primary_language__name', 'status', 'event_management_code', 
    'online_registration_code', 'contact_phone1', 'contact_email', 
    'created', 'id']

    if not queryset:
        schedules = ProgramSchedule.objects.filter(start_date__gte=(DateDeux.today()-60)).filter(hidden=False).filter(program__admin=False).order_by('center__zone__zone_name', '-start_date')
    else:
        schedules = queryset.order_by('center__zone__zone_name', '-start_date')

    schedules = schedules.annotate(final_event_name=Case(
        When(program__name=Value("Special Event"), then="event_name"),
        default="program__name")
    )

    schedules = schedules.values(*column_list)

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
        ('final_event_name', 'Program Type'),
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


def get_iyc_schedules(zone_name="Isha Yoga Center"):
    schedules = ProgramSchedule.objects.filter(start_date__gte=(DateDeux.today()-60)).filter(center__zone__zone_name=zone_name).order_by('-start_date')

    schedules = get_schedules(schedules)
    return schedules


def write_file(json_data, full_file_path):
    json_string = json.dumps(json_data, indent=4, sort_keys=True)
    f = open(full_file_path, "w")
    f.write(json_string)
    f.close()



class Command(BaseCommand):
    help = "Sync schedules. See gsync.settings for definitions"

    def handle(self, *args, **options):
        # use this for prod
        output_path = path_join(settings.MEDIA_ROOT, "schedules")

        # use this for test
        output_path = "/tmp"

        schedule_output_file = path_join(output_path, "schedules.json")
        enrollment_output_file = path_join(output_path, "enrollments.json")
        iyc_output_file = path_join(output_path, "iyc_schedules.json")

        schedules = get_schedules()
        enrollments = get_enrollments(schedules)
        iyc_schedules = get_iyc_schedules()

        write_file(schedules, schedule_output_file)
        write_file(enrollments, enrollment_output_file)
        write_file(iyc_schedules, iyc_output_file)


        print("JSONs ==>  ", schedule_output_file, 
                            enrollment_output_file,
                            iyc_output_file)