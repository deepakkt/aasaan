# -*- coding: utf-8 -*-

"""
Create ORS programs for newly defined programs in Aasaan
"""
from datetime import date

from django.core.management.base import BaseCommand

from communication.api import stage_pushover, send_communication
from schedulemaster.models import ProgramSchedule

from collections import Counter


class Command(BaseCommand):
    help = "Set programs with past date as 'registration closed'"

    def handle(self, *args, **options):

        count = Counter()
        today = date.today()

        for each_schedule in ProgramSchedule.objects.filter(end_date__lt=today, status='RO'):
            print(each_schedule)
            count['updated'] += 1
            each_schedule.status = 'RC'
            each_schedule.save()

        send_communication("Pushover", stage_pushover(communication_message="%d past due programs updated! " % count['updated'],
                                                      role_groups = ["Aasaan Admin"]))
