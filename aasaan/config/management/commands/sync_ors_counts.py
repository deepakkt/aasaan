# -*- coding: utf-8 -*-

"""
Create ORS programs for newly defined programs in Aasaan
"""
from datetime import date

from django.core.management.base import BaseCommand

from schedulemaster.models import ProgramSchedule, ProgramScheduleCounts, \
 ProgramCountMaster
from config.ors.ors import ORSInterface
from config.models import get_configuration
from django.conf import settings


def _return_category(category_name, category_set):
    for each_category in category_set:
        if each_category.category.count_category == category_name:
            return each_category

    return None

def _create_or_update(fields, values, schedule):
    _fvs = zip(fields, values)
    categories = schedule.programschedulecounts_set.all()

    for field, value in _fvs:
        _base_cat = ProgramCountMaster.objects.get(count_category=field)
        _model_cat = _return_category(field, categories) or ProgramScheduleCounts()

        _model_cat.program = schedule
        _model_cat.category = _base_cat
        _model_cat.value = value

        _model_cat.save()


class Command(BaseCommand):
    help = "Set programs with past date as 'registration closed'"

    def add_arguments(self, parser):
        parser.add_argument('year', nargs='?', type=int)
        parser.add_argument('month', nargs='?', type=int)


    def handle(self, *args, **options):
        _fields_to_update = ["ORS Participant Count", "ORS Absent Count", "ORS Online Count"]
        _workflow_fields_to_update = ["ORS Address List Count", "ORS VIFO Count"]
        ors_interface = ORSInterface(settings.ORS_USER, settings.ORS_PASSWORD)
        ors_interface.authenticate()

        workflow_programs = get_configuration('ORS_WORKFLOW_PROGRAMS').split('\r\n')

        if options['year']:
            year = options['year']
            month = options['month']
            _start_date = date(year, month, 1)
            _end_date = date.fromordinal(date(year, month + 1, 1).toordinal() - 1)
            _schedules = ProgramSchedule.objects.filter(start_date__gte=_start_date,
                                                        end_date__lte=_end_date)
        else:
            reference_date = date.fromordinal(date.toordinal(date.today()) - 50)
            _schedules = ProgramSchedule.objects.filter(start_date__gte=reference_date)


        for each_schedule in _schedules:
            if not each_schedule.event_management_code:
                continue

            if each_schedule.event_management_code == "FAILED":
                continue

            if not len(each_schedule.event_management_code) == 9:
                continue

            print(each_schedule)

            ors_summary = ors_interface.get_ors_summary(each_schedule.event_management_code)

            if not ors_summary:
                continue

            print(ors_summary)

            _create_or_update(_fields_to_update, (ors_summary['Total'], ors_summary['Absent'],
                                                    ors_summary['Online']), each_schedule)

            if each_schedule.program.name in workflow_programs:
                _create_or_update(_workflow_fields_to_update, (ors_summary['Address List'], 
                                ors_summary['VIFO']),
                                each_schedule)

            
