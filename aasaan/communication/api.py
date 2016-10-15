import requests
from sys import modules
from functools import partial

from django.core.exceptions import ValidationError, ObjectDoesNotExist, ImproperlyConfigured
from django.core.mail import get_connection
from django.core.mail.message import EmailMultiAlternatives
from django.conf import settings

from .settings import smscountry_parms as base_smscountry_parms
from .settings import COMMUNICATION_CONTEXTS, COMMUNICATION_TYPES, RECIPIENT_VISIBILITY
from . import settings as comm_settings
from .models import Payload, PayloadDetail, CommunicationProfile

from contacts.models import RoleGroup

import sendgrid
import markdown

try:
    import django_rq
except (ImportError, ImproperlyConfigured):
    pass


def _get_param(param_name):
    try:
        param_value = getattr(comm_settings, param_name)
    except KeyError:
        raise ValidationError("Trying to locate '%s' parameter but could not find it. "
                              "Please define the parameter in settings.py in the communication app" % param_name)

    return param_value


class MessageAdapter(object):
    def __init__(self, *args, **kwargs):
        self._validate_message_key(*args, **kwargs)
        self._setup_profile(*args, **kwargs)
        self.get_connection()

    def _validate_message_key(self, *args, **kwargs):
        self.message_key = kwargs.get('message_key')

        if not self.message_key:
            raise ValidationError('Message key cannot be empty')

        try:
            self.message = Payload.objects.get(communication_hash=self.message_key)
        except ObjectDoesNotExist:
            raise ValidationError("Message key '%s' not found" % (self.message_key))

        if self.message.recipient_count() == 0:
            raise ValidationError("No recipients staged for message key '%s'"
                                  %(self.message_key))

        if not self.message.is_status_pending():
            raise ValidationError("%s is not 'pending'. Restage a fresh message" % self.message)

        self.message_recipients = PayloadDetail.objects.filter(communication=self.message)

        self.communication_type = self.message.communication_type

    def _setup_profile(self, *args, **kwargs):
        profile_name = kwargs.get('profile_name')

        try:
            default_profile = CommunicationProfile.objects.get(communication_type=self.communication_type,
                                                   default=True)
        except ObjectDoesNotExist:
            raise ValidationError('No default email profile found. Mark one profile as default.')

        if profile_name:
            try:
                self.profile = CommunicationProfile.objects.get(communication_type=self.communication_type,
                                                           profile_name=profile_name)
            except ObjectDoesNotExist:
                self.profile = default_profile
        else:
            self.profile = default_profile

    def get_connection(self):
        """
        inheriting class to set this up. assign self.connection at end of function
        """
        pass

    def close_connection(self):
        """
        Close connection here
        """
        pass

    def validate_message(self):
        """
        Place validations prior to sending the message here
        """
        pass

    def load_communication_settings(self):
        """
        Load adapter specific settings here. One important variable
        the loader needs to set is self.loop_individual_recipient.
        Set other settings here which can be used by methods later
        in the workflow
        """
        self.message_send_exceptions = None

    def setup_initial_adapter_message(self):
        """
        This is the hook to setup the communication adapter specific message
        object
        """
        self.adapter_message = None

    def setup_final_adapter_message(self, *args, **kwargs):
        """
        Use this hook to setup the final message that will go out through the
        communication channel
        """
        pass

    def send_adapter_communication(self):
        """
        Setup the actual logic to send the message via the adapter
        """
        pass

    def send_message(self):
        try:
            connection = self.connection
        except NameError:
            raise ValidationError("No valid connection present to send message")
        else:
            connection = None

        self.load_communication_settings()
        self.validate_message()

        try:
            looper = self.loop_individual_recipient
        except NameError:
            raise ValidationError("'loop_individual_recipient' flag was not found. The default adapter "
                                  "expects the inheritor to set this flag. Set this flag in the "
                                  "'load_communication_settings' method")
        else:
            del looper

        self.setup_initial_adapter_message()
        self.message.set_in_progress()
        self.message.save()
        error_free = True
        raised_exception = None

        if self.loop_individual_recipient:
            for each_recipient in self.message_recipients:
                self.setup_final_adapter_message(recipient=each_recipient)

                try:
                    self.send_adapter_communication()
                    each_recipient.set_success()
                    each_recipient.set_send_time()
                    each_recipient.communication_status_message = 'Success!'
                    each_recipient.save()
                except self.message_send_exceptions as e:
                    raised_exception = e
                    each_recipient.set_error()
                    each_recipient.communication_status_message = 'Error: %s' % (e.args[0])
                    each_recipient.save()
                    error_free = False
        else:
            self.setup_final_adapter_message()
            try:
                self.send_adapter_communication()
                for each_recipient in self.message_recipients:
                    each_recipient.set_success()
                    each_recipient.set_send_time()
                    each_recipient.save()
            except self.message_send_exceptions as e:
                error_free = False
                raised_exception = e
                for each_recipient in self.message_recipients:
                    each_recipient.set_error()
                    each_recipient.communication_status_message = 'Error: %s' % (e.args[0])
                    each_recipient.save()

        if error_free:
            self.message.set_success()
            self.message.communication_status_message = 'Message appears to be successfully sent!'
        else:
            self.message.set_error()
            self.message.communication_status_message = raised_exception.args[0]

        self.message.save()

        return self.message.communication_status


class EmailMessageAdapter(MessageAdapter):
    def get_connection(self):
        try:
            connection = get_connection(host=self.profile.smtp_server,
                                        port=self.profile.smtp_port,
                                        username=self.profile.user_name,
                                        password=self.profile.password,
                                        use_tls=self.profile.use_tls,
                                        use_ssl=self.profile.use_ssl)
        except:
            raise ValidationError('Could not setup SMTP connection. Check connectivity or credentials.')

        self.connection = connection

    def close_connection(self):
        self.connection.close()

    def load_communication_settings(self):
        super(EmailMessageAdapter, self).load_communication_settings()
        self.recipient_visibility = self.message.recipient_visibility
        self.default_email_type = _get_param('default_email_type').lower()
        self.loop_individual_recipient = True if \
            self.recipient_visibility == comm_settings.RECIPIENT_VISIBILITY[-1][0] \
            else False
        self.message_send_exceptions = ValidationError
        self._message_munge = markdown.markdown if \
            self.default_email_type == comm_settings.DEFAULT_EMAIL_TYPE[0][0] \
            else (lambda x: x)

    def setup_initial_adapter_message(self):
        self.adapter_message = EmailMultiAlternatives()
        self.adapter_message.subject = self.message.communication_title
        self.adapter_message.from_email = "%s <%s>" % (self.profile.sender_name,
                                                       self.profile.user_name)
        self.adapter_message.body = self._message_munge(self.message.communication_message)
        self.adapter_message.content_subtype = self.default_email_type
        self.adapter_message.connection = self.connection

    def setup_final_adapter_message(self, *args, **kwargs):
        recipient = kwargs.get('recipient')

        if recipient:
            self.adapter_message.to = recipient.communication_recipient
            return

        if self.recipient_visibility == "BCC":
            self.adapter_message.bcc = [x.communication_recipient for
                                          x in self.message_recipients]
        elif self.recipient_visibility == "TO/CC":
            self.adapter_message.to = [self.message_recipients[0].communication_recipient]
            self.adapter_message.cc = [x.communication_recipient for
                                         x in self.message_recipients[1:]]
        elif self.recipient_visibility == "TO/BCC":
            self.adapter_message.to = [self.message_recipients[0].communication_recipient]
            self.adapter_message.bcc = [x.communication_recipient for
                                         x in self.message_recipients[1:]]

    def send_adapter_communication(self):
        try:
            self.adapter_message.send()
        except:
            raise ValidationError('Error sending message ==> %s' % (self.message))


class SendGridMessageAdapter(EmailMessageAdapter):
    def get_connection(self):
        try:
            connection = sendgrid.SendGridClient(self.profile.user_name,
                                                 raise_errors=True)
        except (sendgrid.SendGridClientError, sendgrid.SendGridServerError):
            raise ValidationError('Could not setup SendGrid connection. Check connectivity or credentials.')

        self.connection = connection

    def close_connection(self):
        pass

    def load_communication_settings(self):
        super(SendGridMessageAdapter, self).load_communication_settings()
        self.message_send_exceptions = (sendgrid.SendGridClientError, sendgrid.SendGridServerError)

    def setup_initial_adapter_message(self):
        self.adapter_message = sendgrid.Mail()
        self.adapter_message.set_from('%s <%s>' %(self.profile.sender_name,
                                           self.profile.sender_id))
        self.adapter_message.set_subject(self.message.communication_title)
        self.adapter_message.set_html(self._message_munge(self.message.communication_message))
        self.adapter_message.set_text(self.message.communication_message)

    def setup_final_adapter_message(self, *args, **kwargs):
        recipient = kwargs.get('recipient')

        if recipient:
            self.setup_initial_adapter_message()
            self.adapter_message.add_to(recipient.communication_recipient)
            return

        if self.recipient_visibility == "BCC":
            self.adapter_message.add_bcc([x.communication_recipient for
                                          x in self.message_recipients])
        elif self.recipient_visibility == "TO/CC":
            self.adapter_message.add_to(self.message_recipients[0].communication_recipient)
            self.adapter_message.add_cc([x.communication_recipient for
                                         x in self.message_recipients[1:]])
        elif self.recipient_visibility == "TO/BCC":
            self.adapter_message.add_to(self.message_recipients[0].communication_recipient)
            self.adapter_message.add_bcc([x.communication_recipient for
                                         x in self.message_recipients[1:]])

    def send_adapter_communication(self):
        self.connection.send(self.adapter_message)


class SMSCountryMessageAdapter(MessageAdapter):
    def get_connection(self):
        self.connection = _get_param('smscountry_api_url')
        self.adapter_message = base_smscountry_parms.copy()
        self.adapter_message['user'] = self.profile.user_name
        self.adapter_message['passwd'] = self.profile.password

    def validate_message(self):
        message_length = len(self.message.communication_message)
        if message_length > self.allowed_sms_length:
            raise ValidationError('SMS length exceeds allowed limit. '
                                  'Allowed ==> %d, '
                                  'Provided ==> %d' % (self.allowed_sms_length,
                                                    message_length))

    def load_communication_settings(self):
        self.allowed_sms_length = _get_param('sms_length_limit')
        self.loop_individual_recipient = True
        self.message_send_exceptions = ValidationError

    def setup_initial_adapter_message(self):
        self.adapter_message['message'] = self.message.communication_message

    def setup_final_adapter_message(self, *args, **kwargs):
        self.adapter_message['mobilenumber'] = kwargs.get('recipient').communication_recipient

    def send_adapter_communication(self):
        sms_request = requests.get(self.connection, params=self.adapter_message)

        if sms_request.text[:3] == "OK:":
            pass
        else:
            raise ValidationError('SMS send failed for %s. '
                                  'Recipient at failure was \'%s\'' % (self.message,
                                                                       self.adapter_message['mobilenumber']))


class PushoverMessageAdapter(MessageAdapter):
    def get_connection(self):
        self.connection = _get_param('pushover_api_url')

    def load_communication_settings(self):
        self.loop_individual_recipient = True
        self.message_send_exceptions = ValidationError

    def setup_initial_adapter_message(self):
        self.adapter_message = dict()
        self.adapter_message['message'] = self.message.communication_message
        self.adapter_message['token'] = self.profile.user_name

    def setup_final_adapter_message(self, *args, **kwargs):
        self.adapter_message['user'] = kwargs.get('recipient').communication_recipient

    def send_adapter_communication(self):
        pushover_request = requests.post(self.connection, params=self.adapter_message)

        if pushover_request.status_code != 200:
            raise ValidationError('Could not push for user %s. Error message received was'
                                  '"%s"' %(self.adapter_message['user'], pushover_request.text))


def stage_communication(communication_type="EMail", role_groups=None,
                        communication_recipients=None, communication_context="Communication",
                        communication_title="", communication_message="",
                        recipient_visibility=""):

    if not (role_groups or communication_recipients):
        raise ValidationError("Specify at least one recipient")

    if communication_type not in [x[0] for x in COMMUNICATION_TYPES]:
        raise ValidationError("Invalid communication type '%s'" % communication_type)

    if communication_context not in [x[0] for x in COMMUNICATION_CONTEXTS]:
        raise ValidationError("Invalid communication context '%s'" % communication_context)

    if not (communication_title and communication_message):
        raise ValidationError("Specify message and title")

    if not recipient_visibility:
        recipient_visibility = RECIPIENT_VISIBILITY[-1][0]
    else:
        if recipient_visibility not in [x[0] for x in RECIPIENT_VISIBILITY]:
            raise ValidationError("Invalid recipient visibility '%s'" % recipient_visibility)

    message = Payload()
    message.communication_title = communication_title
    message.communication_message = communication_message
    message.communication_type = communication_type
    message.communication_context = communication_context
    message.recipient_visibility = recipient_visibility
    message.save()

    contact_set = []
    contact_field_map = dict(zip([x[0] for x in COMMUNICATION_TYPES],
                            ['primary_email', 'primary_mobile', 'primary_email', 'pushover_token']))

    for each_role in (role_groups or []):
        curr_role_group = RoleGroup.objects.get(role_name=each_role)
        contact_set.extend(filter(bool, [getattr(x, contact_field_map[communication_type])
                            for x in curr_role_group.contacts]))

    contact_set.extend(communication_recipients or [])

    for each_contact in sorted(list(set(contact_set))):
        new_recipient = PayloadDetail()
        new_recipient.communication = message
        new_recipient.communication_recipient = each_contact
        new_recipient.save()

    return message.communication_hash


def send_communication(communication_type="EMail",
                       message_key="", *args, **kwargs):
    this_module = modules[__name__]
    api_full_name = _get_param('communication_dispatcher')[communication_type]
    api_name = api_full_name.split('.')[-1]
    message_api = getattr(this_module, api_name)

    if not message_api:
        raise ValidationError("No API has been defined for communication type '%s'"
                              % (communication_type))

    message_container = message_api(message_key=message_key)

    if settings.ASYNC:
        django_rq.enqueue(message_container.send_message)
        message_status = "Complete"
    else:
        message_status = message_container.send_message()


    if message_status != comm_settings.COMMUNICATION_STATUS[2][0]:
        raise ValidationError("Message send for key '%s' does not report success. "
                              "Review communication status inside payload"
                              "for error details" % (message_key))

    return message_status

# setup canned functions for various scenarios
stage_pushover = partial(stage_communication, communication_type="Pushover",
                         communication_context = "Transactional",
                         communication_title = "Pushover Notification")
stage_email_transactional = partial(stage_communication, communication_type="EMail",
                                       communication_context = "Transactional",
                                    communication_title = "Email Notification")
stage_email = partial(stage_communication, communication_type="EMail",
                                       communication_context = "Communication")
stage_sendgrid = partial(stage_communication, communication_type="SendGrid",
                                       communication_context = "Communication")
stage_sendgrid_transactional = partial(stage_communication, communication_type="SendGrid",
                                       communication_context = "Transactional",
                                    communication_title = "Sendgrid Notification")
stage_sms = partial(stage_communication, communication_type="SMS",
                                       communication_context = "Communication")
stage_sms_transactional = partial(stage_communication, communication_type="SMS",
                                       communication_context = "Transactional",
                                       communication_title = "SMS Notification")
