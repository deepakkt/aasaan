# -*- coding: utf-8 -*-

from datetime import datetime

from django.core.management.base import BaseCommand

from django_rq import enqueue

from notify.models import Notifier

from notify.api.sendgrid_api import send_email
from config.config_utils import rq_present



class Command(BaseCommand):
    help = "Send all communications under 'scheduled'"

    def handle(self, *args, **options):
        _dryrun=False
        
        for _notify in Notifier.objects.filter(notify_status='Scheduled'):
            print(_notify.notify_title)
            if rq_present():
                enqueue(send_email, notify_id=_notify.id, dryrun=_dryrun)
            else:
                send_email(notify_id=_notify.id, dryrun=_dryrun)