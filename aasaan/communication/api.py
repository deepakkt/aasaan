from hashlib import md5
import requests
import markdown
from datetime import datetime

from django.conf import settings
from django.core.exceptions import ValidationError, ObjectDoesNotExist

import communication.settings as comm_settings
from communication.settings import communication_dispatcher
from communication.models import Payload, PayloadDetail


def generate_message_key(*args, **kwargs):
    """Allow user to specify custom keywords and arguments
    to generate a custom hash as per application logic
    """
    hash_digest = md5()

    for value in args:
        hash_digest.update(bytes(repr(value), 'utf-8'))

    for key in kwargs:
        hash_digest.update(bytes(repr(kwargs[key]), 'utf-8'))

    return hash_digest.hexdigest()


def send_email(message=None):
    pass


def send_smscountry_sms(message=None):
    def _get_param(param_name):
        try:
            param_value = getattr(comm_settings, param_name)
        except AttributeError:
            raise ValidationError("Trying to locate '%s' parameter but could not find it. "
                                  "Please define the parameter in settings.py in the communication app" % param_name)

        return param_value

    message_recipients = PayloadDetail.objects.filter(communication=message)
    smscountry_parms = settings.smscountry_parms
    message.set_in_progress()

    sms_length_limit = _get_param('sms_length_limit')
    smscountry_api_url = _get_param('smscountry_api_url')

    if len(message.communication_message) > sms_length_limit:
        raise ValidationError("Message length over limit. Defined limit is %d while message is %d" %(sms_length_limit,
                            len(message.communication_message)))

    smscountry_parms['message'] = message.communication_message
    error_free = True

    for each_recipient in message_recipients:
        each_recipient.set_in_progress()

        smscountry_parms['mobilenumber'] = each_recipient.communication_recipient

        sms_request = requests.get(smscountry_api_url, parms=smscountry_parms)

        each_recipient.communication_status_message = sms_request.text
        each_recipient.send_time = datetime.now()

        if sms_request.text[:3] == "OK:":
            each_recipient.set_success()
        else:
            error_free = False
            each_recipient.set_error()

    if error_free:
        message.set_success()
    else:
        message.set_error()

    return message.communication_status


def _get_dispatcher(communication_type='EMail'):
    import sys
    self_module = sys.modules[__name__]

    try:
        return getattr(self_module, communication_dispatcher[communication_type])
    except AttributeError:
        return None


def send_communication(message_key=""):
    if not message_key:
        raise ValidationError("Message key cannot be empty")

    try:
        message = Payload.objects.get(communication_hash=message_key)
    except ObjectDoesNotExist:
        raise ValidationError("Message key '%s' does not exist" %(message_key))

    message_api = _get_dispatcher(message.communication_type)

    if not message_api:
        raise ValidationError("No API has been defined for communication type '%s'"
                              %(message.communication_type))

    if message.recipient_count() == 0:
        raise ValidationError("No recipients staged for message key '%s'"
                              %(message.communication_hash))

    if not message.is_status_pending():
        raise ValidationError("%s is not 'pending'. Restage a fresh message" % message)

    return message_api(message)

if __name__ == "__main__":
    print(generate_message_key(1, 2, name='Harish', age=45, gender='M'))
    print(_get_dispatcher('SMS'))