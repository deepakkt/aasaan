from django.core.management.base import BaseCommand

from communication.models import Payload, PayloadDetail
import communication.api as api

import random

class Command(BaseCommand):
    help = 'Send test SMS to ensure API works'

    def handle(self, *args, **options):
        api.send_communication("de63e90a6c0c726b4b0a2362fa468dca")

        #self.stdout.write('%s' % (test_message.communication_status))
