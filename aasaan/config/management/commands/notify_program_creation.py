# -*- coding: utf-8 -*-
from datetime import date, datetime

from django.core.management.base import BaseCommand
from django.conf import settings
from schedulemaster.models import ProgramSchedule

from config.models import get_configurations

from utils.datedeux import DateDeux
import sendgrid

from .notify_utils import setup_sendgrid_connection, process_notification


class Command(BaseCommand):
    help = "Notify configured recipients about new programs scheduled"

    def add_arguments(self, parser):
        parser.add_argument('programid', nargs='?', type=int)

    def handle(self, *args, **options):
        sendgrid_key = settings.SENDGRID_KEY
        sendgrid_connection = setup_sendgrid_connection(sendgrid_key)
        configurations = get_configurations('NOTIFY')

        if options['programid']:
            schedule = ProgramSchedule.objects.get(id=options['programid'])
            notification = process_notification(schedule, configurations, 
                                                sendgrid_connection, 
                                                "NOTIFY_NEW_PROGRAM_TEMPLATE")
            if notification:
                return "Notification sent successfully!"
            else:
                return "Notification not sent. Check configurations for potential issue"

        _yesterday = DateDeux.today() - 1

        for schedule in ProgramSchedule.objects.filter(created__date=_yesterday):
            print(schedule)
            notification = process_notification(schedule, configurations, 
                                                sendgrid_connection, 
                                                "NOTIFY_NEW_PROGRAM_TEMPLATE")
            if notification:
                print("Notification sent successfully!")
            else:
                print("Notification not sent. Check configurations for potential issue")
