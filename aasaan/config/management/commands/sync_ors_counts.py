# -*- coding: utf-8 -*-

"""
Create ORS programs for newly defined programs in Aasaan
"""
from datetime import date

from django.core.management.base import BaseCommand

from schedulemaster.models import ProgramSchedule, ProgramScheduleCounts, \
 ProgramCountMaster
from config.ors.ors import ORSInterface
from django.conf import settings


def _return_category(category_name, category_set):
    for each_category in category_set:
        if each_category.category.count_category == category_name:
            return each_category

    return None

class Command(BaseCommand):
    help = "Set programs with past date as 'registration closed'"

    def handle(self, *args, **options):
        ors_total = ProgramCountMaster.objects.get(count_category="ORS Participant Count")
        ors_absent = ProgramCountMaster.objects.get(count_category="ORS Absent Count")
        ors_online = ProgramCountMaster.objects.get(count_category="ORS Online Count")
        ors_interface = ORSInterface(settings.ORS_USER, settings.ORS_PASSWORD)
        ors_interface.authenticate()

        if args:
            year = int(args[0])
            month = int(args[1])
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

            schedule_categories = each_schedule.programschedulecounts_set.all()

            ors_participant_count = _return_category("ORS Participant Count", schedule_categories)
            ors_absent_count = _return_category("ORS Absent Count", schedule_categories)
            ors_online_count = _return_category("ORS Online Count", schedule_categories)

            if not ors_participant_count:
                ors_participant_count = ProgramScheduleCounts()
                ors_participant_count.program = each_schedule
                ors_participant_count.category = ors_total
            ors_participant_count.value = ors_summary["Total"]

            if not ors_absent_count:
                ors_absent_count = ProgramScheduleCounts()
                ors_absent_count.program = each_schedule
                ors_absent_count.category = ors_absent
            ors_absent_count.value = ors_summary["Absent"]

            if not ors_online_count:
                ors_online_count = ProgramScheduleCounts()
                ors_online_count.program = each_schedule
                ors_online_count.category = ors_online
            ors_online_count.value = ors_summary["Online"]


            ors_participant_count.save()
            ors_absent_count.save()
            ors_online_count.save()


