from datetime import date, datetime

from django.utils.text import slugify

from schedulemaster.models import ProgramSchedule
from config.models import get_configurations
from contacts.models import IndividualContactRoleCenter, IndividualContactRoleZone

from notify.api.sendgrid_api import stage_classic_notification

from utils.datedeux import DateDeux

import traceback

def build_template_dict(schedule):
    _template_dict = dict()

    _url_prefix = "http://www.ishayoga.org/en/component/program/?task=details&program_id=" if schedule.online_registration_code else ""
    _template_dict['TEMPLATE_START_DATE'] = DateDeux.frompydate(schedule.start_date).dateformat("dd-mmm-yyyy")
    _template_dict['TEMPLATE_ORS_CODE'] = schedule.event_management_code
    _template_dict['TEMPLATE_JOOMLA_CODE'] = schedule.online_registration_code
    _template_dict['TEMPLATE_FINANCE_NAME'] = schedule.tally_name
    _template_dict['TEMPLATE_CONTACT'] = "%s @ %s, %s" % (schedule.contact_name,
                                                            schedule.contact_email,
                                                            schedule.contact_phone1)
    _template_dict['TEMPLATE_WEB_URL'] =  _url_prefix + schedule.online_registration_code
    _template_dict['TEMPLATE_NOTIFICATION_TIMESTAMP'] = datetime.now().isoformat()
    _template_dict['TEMPLATE_PROGRAM_NAME'] = schedule.program.name
    _template_dict['TEMPLATE_LOCATION'] = "%s, %s" % (schedule.center.center_name,
                                                        schedule.center.zone.zone_name)

    return _template_dict


def build_email_body(templates, mailbody):
    _mailbody = mailbody[:]
    for template in templates:
        _mailbody = _mailbody.replace(template, templates[template])

    return _mailbody


def build_config_heirarchy(heirarchy, prefix="NOTIFY", suffix="TARGET"):
    _config_heirarchy = []
    _build_heirarchy = lambda h: prefix + "_" + slugify(h).upper().replace("-", "_") + "_" + suffix
    _previous = ""

    for h in heirarchy:
        _previous += " " + h
        _config_heirarchy.append(_build_heirarchy(_previous))
    return tuple(_config_heirarchy)


def return_lowest_heirarchy(heirarchy, configurations):
    _heirarchy_list = list(heirarchy)
    _heirarchy_list.reverse()
    _config_pull = lambda x: configurations.get(x, "")
    results = [x for x in map(_config_pull, _heirarchy_list) if x]

    return results[0] if results else ""


def build_config_email_list(config, schedule):
    config_list = config.split("\r\n")

    email_list = []
    _fnmail = lambda x: x.full_name + "|" + x.primary_email

    for config_item in config_list:
        _subitems = config_item.split(':')

        if _subitems[0].lower() == "email":
            email_list.append(_subitems[-1])
            continue

        if _subitems[0].lower() == "zone":
            zone_roles = IndividualContactRoleZone.objects.filter(zone=schedule.center.zone,
                                                                role__role_name=_subitems[-1])
            email_sublist = []
            for zone_role in zone_roles:
                email_sublist.append(_fnmail(zone_role.contact))
            email_sublist = list(set(email_sublist))
            email_list.extend(email_sublist)
            continue

        if _subitems[0].lower() == "center":
            center_roles = IndividualContactRoleCenter.objects.filter(center=schedule.center,
                                                                    role__role_name=_subitems[-1])
            email_sublist = []
            for center_role in center_roles:
                email_sublist.append(_fnmail(center_role.contact))
            email_sublist = list(set(email_sublist))
            email_list.extend(email_sublist)

    return tuple(set(email_list))


def dispatch_notification(msg_from, msg_to, msg_subject, msg_body, connection, msg_cc=[], msg_bcc=[]):
    """
        16-May-2018, deprecated in favor of notify.api.sendgrid_api
        Use stage_classic_notification
    """
    try:
        #msg = sendgrid.Mail()
        msg = dict()

        msg.set_from(msg_from)
        msg.set_subject(msg_subject)
        msg.set_html(msg_body)
        if msg_cc:
            msg.cc = msg_cc
        if msg_bcc:
            msg.bcc = msg_bcc

        for each_to in msg_to:
            print("sending email to ", each_to, " ...")
            msg.to = each_to
            connection.send(msg)
        return True
    except:
        return False


def setup_sendgrid_connection(sendgrid_key):
    """
        16-May-2018, deprecated in favor of notify.api.sendgrid_api
        Use send_mail
    """    
    # return sendgrid.SendGridClient(sendgrid_key)
    return None


def process_notification(schedule, configurations,
                        connection,
                        email_template="NOTIFY_NEW_PROGRAM_TEMPLATE"):
    _notify_zone_list = configurations.get(build_config_heirarchy([schedule.program.name], suffix='ZONES')[0])

    if not _notify_zone_list:
        print('Program not configured for notification')
        return False

    _notify_zone_list = _notify_zone_list.split("\r\n")

    if schedule.center.zone.zone_name not in _notify_zone_list:
        print('Zone not configured for notification of this program')
        return False

    _config_heirarchy = build_config_heirarchy([schedule.program.name,
                                                schedule.center.zone.zone_name,
                                                schedule.center.center_name])

    _notification_config = return_lowest_heirarchy(_config_heirarchy, configurations)

    if not _notification_config:
        print('No notification target configured for this program')
        return False

    _emails = build_config_email_list(_notification_config, schedule)

    if not _emails:
        print('No emails found to send notification :-(')
        return False

    _template_dict = build_template_dict(schedule)

    message_body = configurations.get(email_template)

    if not message_body:
        print('Message body is empty! Configure email template')
        return False

    message_body = build_email_body(_template_dict, message_body)

    msg_from = configurations.get("NOTIFY_EMAIL_FROM_ADDRESS")
    msg_subject = configurations.get(email_template + "_SUBJECT")

    if not msg_subject:
        print('Subject for notification is not configured!')
        return False

    if not msg_from:
        print('Sender from name for notification is not configured!')
        return False

    msg_subject = build_email_body(_template_dict, msg_subject)

    stage_classic_notification("Program Notification", msg_from,
                                _emails, list(), msg_subject,
                                message_body, list(),
                                sender_in_cc=False)

    return True                            
