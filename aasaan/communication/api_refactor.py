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
    SendGridProfile, CommunicationProfile
import sendgrid


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
            self.message = Payload.object.get(message_key=self.message_key)
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

    def _setup_initial_adapter_message(self):
        """
        This is the hook to setup the communication adapter specific message
        object
        """
        self.adapter_message = None

    def _setup_final_adapter_message(self, *args, **kwargs):
        """
        Use this hook to setup the final message that will go out through the
        communication channel
        """
        pass

    def _send_adapter_communication(self):
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

        self.validate_message()
        self.load_communication_settings()

        try:
            looper = self.loop_individual_recipient
        except NameError:
            raise ValidationError("'loop_individual_recipient' flag was not found. The default adapter "
                                  "expects the inheritor to set this flag. Set this flag in the "
                                  "'load_communication_settings' method")
        else:
            del looper

        self._setup_initial_adapter_message()
        self.message.set_in_progress()
        self.message.save()
        error_free = True

        if self.loop_individual_recipient:
            for each_recipient in self.message_recipients:
                self._setup_final_adapter_message(recipient=each_recipient)

                try:
                    self._send_adapter_communication()
                    each_recipient.set_success()
                    each_recipient.communication_send_time = datetime.now()
                    each_recipient.save()
                except self.message_send_exceptions as e:
                    each_recipient.set_error()
                    each_recipient.save()
                    error_free = False
        else:
            self._setup_final_adapter_message()
            try:
                self._send_adapter_communication()
                for each_recipient in self.message_recipients:
                    each_recipient.set_success()
                    each_recipient.communication_send_time = datetime.now()
                    each_recipient.save()
            except self.message_send_exceptions as e:
                error_free = False
                for each_recipient in self.message_recipients:
                    each_recipient.set_error()
                    each_recipient.save()

        if error_free:
            self.message.set_success()
        else:
            self.message.set_error()
        message.save()


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



class SendGridMessageAdapter(MessageAdapter):
    pass

class SMSCountryMessageAdapter(MessageAdapter):
    pass