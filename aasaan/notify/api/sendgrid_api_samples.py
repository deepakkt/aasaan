from copy import deepcopy
import urllib
import os.path

import sendgrid
from .base64_api import get_base64_string as gb64
from sendgrid.helpers.mail import Email, Content, Mail, Attachment

from python_http_client.exceptions import BadRequestsError

from django.conf import settings


# python_http_client.exceptions.BadRequestsError: HTTP Error 400: Bad Request

def build_fnln_contact(individual_contact):
    """
        Expected parameter format for individual_contact
        ('My Name', 'myname@gmail.com')

        Sample output: 
        {'email': 'myname@gmail.com', 'name': 'My Name'}
    """
    return {
        "email": individual_contact[-1],
        "name": individual_contact[0]
    }


def get_mail_template():
    return {
        "personalizations": [
            {
            "to": [
            ],
            "cc": [
            ],        
            "bcc": [
            ],        
            "subject": ""
            }
        ],
        "from": {
        },
        "content": [
            {
            "type": "text/html",
            "value": ""
            }
        ],
        "attachments": [
        ]
    }

def cleanup_email_template(mail_chunk):
    """
        Remove unused personalizations and attachments
    """
    # make a copy. don't modify original reference
    _mail_chunk = deepcopy(mail_chunk)

    if not _mail_chunk['attachments']:
        _mail_chunk.pop('attachments')

    if not _mail_chunk['personalizations'][0]['cc']:
        _mail_chunk['personalizations'][0].pop('cc')

    if not _mail_chunk['personalizations'][0]['bcc']:
        _mail_chunk['personalizations'][0].pop('bcc')

    return _mail_chunk

def add_email_recipient(receive_context,
                    fnln_contact,
                    mail_chunk=get_mail_template(),
                    replace=False):
    """
        receive_context = to/cc/bcc
        fnln_contact = mandatory contact, needs to be compatible with output of build_fnln_contact 
        mail_chunk = pre-built mail content. default not recommended
        replace = True, replace fnln_contact into receive_context
                    False, append to it. False should be the normal use case

        mail_chunk is assumed to comply with template output by get_mail_template()                    
        errors in parsing return input mail_chunk as is
    """

    # make a copy. don't modify original reference
    _mail_chunk = deepcopy(mail_chunk)

    try:
        _recipient = _mail_chunk["personalizations"][0][receive_context]

        if replace:
            _recipient = [dict(fnln_contact)]
            _mail_chunk["personalizations"][0][receive_context] = _recipient
        else:
            _recipient.append(dict(fnln_contact))
    except:
        # some parsing error, in such case send the original template back
        return mail_chunk

    return _mail_chunk


def set_from_contact(fnln_contact, mail_chunk=get_mail_template()):
    # make a copy. don't modify original reference
    _mail_chunk = deepcopy(mail_chunk)
    _mail_chunk["from"] = dict(fnln_contact)
    return _mail_chunk


def set_subject(subject, mail_chunk=get_mail_template()):
    # make a copy. don't modify original reference
    _mail_chunk = deepcopy(mail_chunk)
    _mail_chunk["personalizations"][0]["subject"] = subject
    return _mail_chunk

def set_content(content, mail_chunk=get_mail_template()):
    # make a copy. don't modify original reference
    _mail_chunk = deepcopy(mail_chunk)

    try:
        _mail_chunk["content"][0]["value"] = content
    except:
        # some parsing error, in such case send the original template back
        return mail_chunk

    return _mail_chunk        


def add_attachment(filename, mail_chunk, replace=False):
    """
        filename should contain full qualified path
    """
    # make a copy. don't modify original reference
    _mail_chunk = deepcopy(mail_chunk)

    try:
        _file_chunk = gb64(filename)
    except:
        # some parsing error, in such case send the original template back
        return mail_chunk

    _fn = lambda fn: os.path.split(fn)[-1]

    _att = {
        "content": _file_chunk,
        "disposition": "attachment",
        "filename": _fn(filename)
    }

    if replace:
        _mail_chunk["attachments"] = [_att]
    else:
        _mail_chunk["attachments"].append(_att)

    return _mail_chunk


def send_email(mail_chunk, apikey=None):
    if (not apikey):
        try:
            apikey = settings.SENDGRID_KEY
        except:
            return (False, "Could not acquire API Key for Sendgrid")

    try:
        sg = sendgrid.SendGridAPIClient(apikey=apikey)
    except:
        return (False, "Could not connect to sendgrid. Check API Key")

    try:
        response = sg.client.mail.send.post(request_body=mail_chunk)
        success = True
        _errors = "Send appears successful"

        print(response.status_code)
        print(response.body)
        print(response.headers)
        
    #except urllib.HTTPError as e:
    except urllib.error.HTTPError as e:
        _errors = e.read()
        success = False

    return (success, _errors)
    


# sample_send_attachment() 