from django.core.management.base import BaseCommand

from communication.models import Payload, PayloadDetail
import communication.api as api

import random

class Command(BaseCommand):
    help = 'Send test SMS to ensure API works'

    def handle(self, *args, **options):
        def _add_recipient(communication, recipient_number):
            new_recipient = PayloadDetail()
            new_recipient.communication = communication
            new_recipient.communication_recipient = recipient_number
            new_recipient.save()

        test_message = Payload()
        test_message.communication_title = "Test SMS"
        test_message.communication_notes = "Testing if the thing is working!"
        test_message.communication_type = "SMS"
        test_message.communication_message = """Namaskaram,
This message is sent via aasaan communication interface.
If you are seeing this, it is working :)
Pranams"""

        test_message.save()

        test_message.communication_hash = api.generate_message_key(test_message, str(random.random()))
        test_message.save()

        _add_recipient(test_message, "9841019409")
        _add_recipient(test_message, "9962060010")
        _add_recipient(test_message, "9487895188")

        api.send_communication(test_message.communication_hash)

        self.stdout.write('%s' % (test_message.communication_status))
