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
        sync.sync_schedules_test()

