# -*- coding: utf-8 -*-

from datetime import datetime

from django.core.management.base import BaseCommand

from config.models import DatabaseRefresh
from config.config_utils import refresh_database_backup, rq_present

from django_rq import enqueue

class Command(BaseCommand):
    help = "Make all latest commits in Master 'live'"

    print("starting deploy")

    def handle(self, *args, **options):
        for refresh_request in DatabaseRefresh.objects.filter(refresh_status='ST'):
            print('processing ', refresh_request.id)
            if rq_present():
                print('queueing into rq')
                enqueue(refresh_database_backup, refresh_request.id)
            else:
                print('executing backup')
                refresh_database_backup(refresh_request.id)
