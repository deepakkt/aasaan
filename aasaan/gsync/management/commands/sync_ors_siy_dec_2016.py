# -*- coding: utf-8 -*-

"""
Sync schedules to google sheet
All definitions are given in gsync.settings
"""

from django.core.management.base import BaseCommand
from gsync.sync import sync_v2 as sync
from communication.api import stage_pushover, send_communication
import sys
from datetime import datetime


class Command(BaseCommand):
    help = "Sync schedules. See gsync.settings for definitions"

    def handle(self, *args, **options):
        #try:
        sync.sync_siy_dec_2016()
        #except:
            #send_communication("Pushover", stage_pushover(communication_message="Sync failed with %s" % sys.exc_info()[0],
               #                                           role_groups = ["Aasaan Admin"]))
            #sys.exit(1)
        #send_communication("Pushover", stage_pushover(communication_message="Sync complete in server %s" % datetime.now().isoformat(),
         #                                             role_groups = ["Aasaan Admin"]))
