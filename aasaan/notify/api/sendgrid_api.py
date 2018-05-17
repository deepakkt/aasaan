from copy import deepcopy
import urllib
from os import unlink
import os.path
from pprint import pprint
from collections import Counter
import json

import sendgrid
from .base64_api import get_base64_string as gb64
from sendgrid.helpers.mail import Email, Content, \
                                    Mail, Attachment, \
                                    Personalization

from python_http_client.exceptions import BadRequestsError

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

from notify.models import Notifier, NotifyContext
from notify.api.resolvers import parse_notifier_roles


SENDGRID_CONNECTION = None

# python_http_client.exceptions.BadRequestsError: HTTP Error 400: Bad Request

def _setup_email(_notify):
    mail = Mail()

    mail.from_email = Email(**_notify.from_email)

    for attachment in _notify.attachment_list():
        _att = Attachment()
        _att.content = gb64(attachment)
        _att.filename = os.path.split(attachment)[-1]
        _att.disposition = "attachment"
        mail.add_attachment(_att)

    mail.add_content(Content("text/html", _notify.message))

    return mail


def setup_connection():
    global SENDGRID_CONNECTION

    try:
        SENDGRID_CONNECTION = sendgrid.SendGridAPIClient(apikey=settings.SENDGRID_KEY)
    except:
        pass

    return SENDGRID_CONNECTION


def send_email_over_http(mail):
    """
        Assumes global variable SENDGRID_CONNECTION
    """
    if not SENDGRID_CONNECTION:
        return (False, "No connection available to send")

    try:
        _payload = repr(mail.get())
        response = SENDGRID_CONNECTION.client.mail.send.post(request_body=mail.get())
    except BadRequestsError:        
        return (False, "Sendgrid reports 400. Failing body: " + _payload)
    except:
        return (False, "Unknown failure. Failing body: " + _payload)

    return (True, "Appears successful. Sendgrid reports status " + str(response.status_code))


def get_recipient_list(_notify):
    role_recepients = parse_notifier_roles(_notify.id)
    to_list = _notify.to_pairs()
    cc_list = _notify.cc_pairs()    

    sending_mode = "Individual" if role_recepients else _notify.sending_mode
    _notify.sending_mode = sending_mode
        
    if not(sending_mode == "Classic"):
        recipient_list = tuple(role_recepients) + to_list + cc_list
        return {"recipients": recipient_list}

    return {"to": to_list, "cc": cc_list}


def get_recipient_objects(_notify):
    _recipients = get_recipient_list(_notify)
    _mail = _setup_email(_notify)
    _pers =  Personalization()
    _pers.subject = _notify.notify_title

    if _recipients.get("to"):
        for _recipient in _recipients["to"]:
            _pers.add_to(Email(**_recipient))
        for _recipient in _recipients["cc"]:
            _pers.add_cc(Email(**_recipient))
        
        _mail.add_personalization(_pers)
        return (_mail,)

    _recipient_list = []

    for _recipient in _recipients.get("recipients", []):
        _pers_copy = deepcopy(_pers)
        _pers_copy.add_to(Email(**_recipient))

        _mail_copy = deepcopy(_mail)
        _mail_copy.add_personalization(_pers_copy)
        _recipient_list.append(_mail_copy)

    return tuple(_recipient_list)


def _delete_attachments(attachment_list):
    for _att in attachment_list:
        try:
            unlink(_att)
        except:
            # do nothing in case of -any- error
            # many things could have happened to the file
            # and it does no harm if the file hangs around
            pass

    return True


def send_email(notify_id, dryrun=False):
    try:
        _notify = Notifier.objects.get(id=notify_id)
    except ObjectDoesNotExist:
        return (False, "Notifier object does not exist")        

    _recipients = get_recipient_objects(_notify)
    
    setup_connection()

    _status = Counter()
    _status_msg = []

    _str_recepient = lambda x: str(x.personalizations[0].tos) + " " + str(x.personalizations[0].ccs)

    for _recipient in _recipients:
        if dryrun:
            pprint(_recipient.get())
        else:
            _success, _msg = send_email_over_http(_recipient)

            if _success:
                _status['Success'] += 1
                _status_msg.append("Success => " + _str_recepient(_recipient))
            else:
                _status['Failure'] += 1
                _status_msg.append("Failure => " + _str_recepient(_recipient) + " " + _msg)

    if not dryrun:
        if _status['Success'] and _status['Failure']:
            _notify.notify_status = "Incomplete"
        elif _status['Success']:
            _notify.notify_status = "Completed"
        else:
            _notify.notify_status = "Failed"

        _notify.detailed_status = "\r\n".join(_status_msg)

    if (_notify.delete_attachments and _notify.notify_status == "Completed"):
        _delete_attachments(_notify.attachment_list())
        _notify.detailed_status = "Attachments deleted! Attempting to send this email again will cause errors! \r\n" + _notify.detailed_status
    
    _notify.save()


def stage_classic_notification(context, from_email, tos, ccs,
                                subject,
                                message, attachments=[],
                                sender_in_cc=True):
    """
        from_email = email or Name|email
        tos = list of email or Name|email
        ccs = list of email or Name|email
        message = html message
        attachments = list of full file paths
    """                                

    _notify = Notifier()
    _notify.notify_title = subject
    _notify.notify_context = NotifyContext.objects.get(context_title=context)
    _notify.notify_status = "Scheduled"
    _notify.notify_type = "Email"
    _notify.sending_mode = "Classic"
    _notify.notify_from =  from_email
    _notify.notify_to = "\r\n".join(tos)
    _notify.notify_cc = "\r\n".join(ccs)
    if sender_in_cc:
        _notify.notify_cc += "\r\n" + from_email
    _notify.message = message
    _notify.attachments = "\r\n".join(attachments)
    _notify.delete_attachments = True
    _notify.save()

    return _notify.id

    



