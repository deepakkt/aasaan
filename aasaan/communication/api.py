import requests
import markdown
from datetime import datetime

from aasaan.settings.config import smscountry_parms as base_smscountry_parms
from django.core.exceptions import ValidationError, ObjectDoesNotExist

from django.core.mail import get_connection, send_mail
from django.core.mail.message import EmailMultiAlternatives

import communication.settings as comm_settings
from .settings import communication_dispatcher
from .models import Payload, PayloadDetail, EmailProfile

def send_email(message=None, *args, **kwargs):
    message_recipients = PayloadDetail.objects.filter(communication=message)
    message.set_in_progress()
    message.save()

    profile = kwargs.get('profile')

    default_profile = EmailProfile.objects.get(default=True)

    if profile is None:
        email_profile = default_profile
    else:
        try:
            email_profile = EmailProfile.objects.get(profile_name=profile)
        except ObjectDoesNotExist:
            email_profile = default_profile

    connection = get_connection(host=email_profile.smtp_server,
                                port=email_profile.smtp_port,
                                username=email_profile.user_name,
                                password=email_profile.password,
                                use_tls=email_profile.use_tls,
                                use_ssl=email_profile.use_ssl)

    email_message = EmailMultiAlternatives()
    email_message.subject = message.communication_title
    email_message.from_email = "%s <%s>" % email_profile.display_name, email_profile.user_name
    email_message.body = markdown.markdown(message.communication_message)
    email_message.attach_alternative(message.communication_message, "text/plain")
    email_message.content_subtype = "html"
    email_message.connection = connection

    error_free = True
    for each_recipient in message_recipients:
        each_recipient.set_in_progress()
        each_recipient.save()

        email_message.to = each_recipient.communication_recipient
        each_recipient.communication_send_time = datetime.now()

        try:
            email_message.send()
            each_recipient.set_success()
        except:
            error_free = False
            each_recipient.set_error()

        each_recipient.save()

    if error_free:
        message.set_success()
    else:
        message.set_error()

    message.save()

    return message.communication_status


def send_smscountry_sms(message=None, *args, **kwargs):
    def _get_param(param_name):
        try:
            param_value = getattr(comm_settings, param_name)
        except KeyError:
            raise ValidationError("Trying to locate '%s' parameter but could not find it. "
                                  "Please define the parameter in settings.py in the communication app" % param_name)

        return param_value

    message_recipients = PayloadDetail.objects.filter(communication=message)
    smscountry_parms = base_smscountry_parms
    message.set_in_progress()
    message.save()

    sms_length_limit = _get_param('sms_length_limit')
    smscountry_api_url = _get_param('smscountry_api_url')

    if len(message.communication_message) > sms_length_limit:
        raise ValidationError("Message length over limit. Defined limit is %d while message is %d" %(sms_length_limit,
                            len(message.communication_message)))

    smscountry_parms['message'] = message.communication_message
    error_free = True

    for each_recipient in message_recipients:
        each_recipient.set_in_progress()
        each_recipient.save()

        smscountry_parms['mobilenumber'] = each_recipient.communication_recipient

        sms_request = requests.get(smscountry_api_url, params=smscountry_parms)

        each_recipient.communication_status_message = sms_request.text
        each_recipient.communication_send_time = datetime.now()

        if sms_request.text[:3] == "OK:":
            each_recipient.set_success()
        else:
            error_free = False
            each_recipient.set_error()

        each_recipient.save()

    if error_free:
        message.set_success()
    else:
        message.set_error()

    message.save()
    return message.communication_status


def _get_dispatcher(communication_type='EMail'):
    import sys
    self_module = sys.modules[__name__]

    try:
        return getattr(self_module, communication_dispatcher[communication_type])
    except KeyError:
        return None


def send_communication(message_key="", *args, **kwargs):
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

    return message_api(message, *args, **kwargs)

if __name__ == "__main__":
    print(_get_dispatcher('SMS'))