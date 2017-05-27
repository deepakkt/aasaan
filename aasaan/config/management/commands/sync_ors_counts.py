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
        ors_interface = ORSInterface(settings.ORS_USER, settings.ORS_PASSWORD)
        ors_interface.authenticate()

        reference_date = date.fromordinal(date.toordinal(date.today()) - 50)

        for each_schedule in ProgramSchedule.objects.filter(start_date__gte=reference_date):
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

            ors_participant_count.save()
            ors_absent_count.save()


