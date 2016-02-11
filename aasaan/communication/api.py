import requests
import markdown
from datetime import datetime

from aasaan.settings.config import smscountry_parms as base_smscountry_parms
from django.core.exceptions import ValidationError, ObjectDoesNotExist

from django.core.mail import get_connection
from django.core.mail.message import EmailMultiAlternatives

import communication.settings as comm_settings
from .settings import communication_dispatcher
from .models import Payload, PayloadDetail, EmailProfile, EmailSetting, \
    SendGridProfile
import sendgrid


def send_sendgrid_email(message=None, *args, **kwargs):
    def _setup_smtp_connection(profile):
        try:
            default_profile = SendGridProfile.objects.get(default=True)
        except ObjectDoesNotExist:
            raise ValidationError('No default SendGrid profile found. Mark one profile as default.')

        if profile is None:
            sendgrid_email_profile = default_profile
        else:
            try:
                sendgrid_email_profile = SendGridProfile.objects.get(profile_name=profile)
            except ObjectDoesNotExist:
                sendgrid_email_profile = default_profile

        try:
            connection = sendgrid.SendGridClient(sendgrid_email_profile.api_key,
                                                 raise_errors=True)
        except (sendgrid.SendGridClientError, sendgrid.SendGridServerError):
            raise ValidationError('Could not setup SendGrid connection. Check connectivity or credentials.')

        return connection, sendgrid_email_profile

    connection, email_profile = _setup_smtp_connection(kwargs.get('profile'))

    message_recipients = PayloadDetail.objects.filter(communication=message)
    message.set_in_progress()
    message.save()

    email_message = sendgrid.Mail()
    email_message.set_from('%s <%s>' %(email_profile.display_name,
                                       email_profile.from_email))
    email_message.set_subject(message.communication_title)
    email_message.set_html(markdown.markdown(message.communication_message))
    email_message.set_text(message.communication_message)

    email_setting = EmailSetting.objects.all()[0]

    if email_setting.recipient_visibility == "BCC":
        email_message.add_bcc([x.communication_recipient for x in message_recipients])
    elif email_setting.recipient_visibility == "TO/CC":
        email_message.add_to([message_recipients[0].communication_recipient])
        email_message.add_cc([x.communication_recipient for x in message_recipients[1:]])
    elif email_setting.recipient_visibility == "TO/BCC":
        email_message.add_to([message_recipients[0].communication_recipient])
        email_message.add_bcc([x.communication_recipient for x in message_recipients[1:]])

    if email_setting.recipient_visibility in ['BCC', 'TO/BCC', 'TO/CC']:
        try:
            connection.send(email_message)
            message.set_success()
            for each_recipient in message_recipients:
                each_recipient.set_success()
                each_recipient.communication_send_time = datetime.now()
                each_recipient.save()
        except (sendgrid.SendGridClientError, sendgrid.SendGridServerError):
            message.set_error()

            for each_recipient in message_recipients:
                each_recipient.set_error()
                each_recipient.save()

        message.save()
        return message.communication_status

    error_free = True

    for each_recipient in message_recipients:
        each_recipient.set_in_progress()
        each_recipient.save()

        email_message.add_to([each_recipient.communication_recipient])

        try:
            connection.send(email_message)
            each_recipient.set_success()
            each_recipient.communication_send_time = datetime.now()
        except (sendgrid.SendGridClientError, sendgrid.SendGridServerError):
            each_recipient.set_error()
            error_free = False

        each_recipient.save()

    if error_free:
        message.set_success()
    else:
        message.set_error()

    message.save()
    return message.communication_status



def send_email(message=None, *args, **kwargs):
    def _setup_smtp_connection(profile):
        try:
            default_profile = EmailProfile.objects.get(default=True)
        except ObjectDoesNotExist:
            raise ValidationError('No default email profile found. Mark one profile as default.')

        if profile is None:
            email_profile = default_profile
        else:
            try:
                email_profile = EmailProfile.objects.get(profile_name=profile)
            except ObjectDoesNotExist:
                email_profile = default_profile

        try:
            connection = get_connection(host=email_profile.smtp_server,
                                        port=email_profile.smtp_port,
                                        username=email_profile.user_name,
                                        password=email_profile.password,
                                        use_tls=email_profile.use_tls,
                                        use_ssl=email_profile.use_ssl)
        except:
            raise ValidationError('Could not setup SMTP connection. Check connectivity or credentials.')

        if not connection:
            raise ValidationError('Could not setup SMTP connection. Check connectivity or credentials.')

        return connection, email_profile

    connection, email_profile = _setup_smtp_connection(kwargs.get('profile'))

    message_recipients = PayloadDetail.objects.filter(communication=message)
    message.set_in_progress()
    message.save()

    email_message = EmailMultiAlternatives()
    email_message.subject = message.communication_title
    email_message.from_email = "%s <%s>" % (email_profile.display_name, email_profile.user_name)
    email_message.body = markdown.markdown(message.communication_message)
    # email_message.attach_alternative(message.communication_message, "text/plain")
    # deepak- this seems to override html content. Not sure why. Commenting out for now.
    email_message.content_subtype = "html"
    email_message.connection = connection

    email_setting = EmailSetting.objects.all()[0]

    if email_setting.recipient_visibility == "BCC":
        email_message.bcc = [x.communication_recipient for x in message_recipients]
    elif email_setting.recipient_visibility == "TO/CC":
        email_message.to = [message_recipients[0].communication_recipient]
        email_message.cc = [x.communication_recipient for x in message_recipients[1:]]
    elif email_setting.recipient_visibility == "TO/BCC":
        email_message.to = [message_recipients[0].communication_recipient]
        email_message.bcc = [x.communication_recipient for x in message_recipients[1:]]

    if email_setting.recipient_visibility in ['BCC', 'TO/BCC', 'TO/CC']:
        try:
            email_message.send()
            message.set_success()

            for each_recipient in message_recipients:
                each_recipient.set_success()
                each_recipient.communication_send_time = datetime.now()
                each_recipient.save()
        except:
            message.set_error()

            for each_recipient in message_recipients:
                each_recipient.set_error()
                each_recipient.save()

        message.save()
        connection.close()
        return message.communication_status

    error_free = True

    for each_recipient in message_recipients:
        each_recipient.set_in_progress()
        each_recipient.save()

        email_message.to = [each_recipient.communication_recipient]

        try:
            email_message.send()
            each_recipient.set_success()
            each_recipient.communication_send_time = datetime.now()
        except:
            each_recipient.set_error()
            error_free = False

        each_recipient.save()

    if error_free:
        message.set_success()
    else:
        message.set_error()

    message.save()
    connection.close()

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