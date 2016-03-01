# -*- coding: utf-8 -*-

"""
Sync schedules to google sheet
All definitions are given in gsync.settings
"""

from django.core.management.base import BaseCommand
from gsync import sync


class Command(BaseCommand):
    help = "Sync schedules. See gsync.settings for definitions"

    def handle(self, *args, **options):
        sync.sync_all()