# -*- coding: utf-8 -*-

from datetime import datetime

from django.core.management.base import BaseCommand

from config.models import DatabaseRefresh
from config.config_utils import refresh_database_backup

try:
    from django_rq import enqueue
except ImportError:
    enqueue = None

class Command(BaseCommand):
    help = "Make all latest commits in Master 'live'"

    print("starting deploy")

    def handle(self, *args, **options):
        for refresh_request in DatabaseRefresh.objects.filter(deploy_status='ST'):
            print('processing ', refresh_request.id)
            if enqueue:
                print('queueing into rq')
                enqueue(refresh_database_backup, refresh_request.id)
            else:
                print('executing backup')
                refresh_database_backup(refresh_request.id)
