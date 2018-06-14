from pprint import pprint
from functools import partial
from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.utils.text import slugify
from django.template import Context, Template

import contacts.models as cm
from notify.models import Notifier


def pair_contact(individual_contact, pair_type="fnln"):
    """
        Valid pair types
        fnln: pair as first name last name ad email
        notifier: pair as first name last name | email
        sendgrid: {"name": name, "email": email}
        as is: no pairing

        individual_contact must be a tuple in the format
        (fn, ln, email)
    """
    _fnln = ' '.join(individual_contact[:2])
    _email = individual_contact[-1]

    if pair_type == "notifier":
        return '|'.join([_fnln, _email])

    if pair_type == "fnln":
        return (_fnln, _email)

    if pair_type == "sendgrid":
        return {"name": _fnln, "email": _email}

    return individual_contact                        


def process_query_pipeline(pipeline, pipeline_fields, pair="fnln"):
    _results = list()
    for pipeline_set in pipeline:
        _model = pipeline_set.get('model', None)
        if not _model: continue

        _queryset = _model.objects.all()
        for each_filter in pipeline_set.get("filters", []):
            for filter_key in each_filter:
                if each_filter[filter_key]:
                    _queryset = _queryset.filter(**{filter_key: each_filter[filter_key]})

        _pipeline_result = _queryset.values_list(*pipeline_fields)

        _results.extend(_pipeline_result)

    _results = tuple(set(_results))
    return tuple(map(partial(pair_contact, pair_type=pair), _results))


def parse_notifier_roles(id, pair="sendgrid"):
    _notifier = Notifier.objects.get(pk=id)

    _zone_list = _notifier.zone_list()
    _role_list = _notifier.role_list()

    if (not _role_list and not _zone_list):
        return []

    pipeline = [
            {
                "model": cm.IndividualContactRoleCenter,
                "filters": [
                    {"center__zone__zone_name__in": _zone_list},
                    {"role__role_name__in": _role_list}
                ]
            },
            {
                "model": cm.IndividualContactRoleZone,
                "filters": [
                    {"zone__zone_name__in": _zone_list},
                    {"role__role_name__in": _role_list}
                ]
            },
        ]

    pipeline_fields = [
            "contact__first_name",
            "contact__last_name",
            "contact__primary_email"
        ]

    _results = process_query_pipeline(pipeline, pipeline_fields,
                                    pair=pair)

    return _results

def remove_email_duplicates(mail_list, func=None):
    if not func:
        _get_email = lambda x: x.split('|')[-1]
    else:
        _get_email = func

    email_list = []
    final_list = []

    for mail in mail_list:
        _mail = _get_email(mail)

        if _mail in email_list:
            continue

        email_list.append(_mail)
        final_list.append(mail)

    return final_list


def remove_email_duplicates_tocc(to_list, cc_list):
    def _append_label(label_name, mail_list):
        return [
            {label_name: _x} for _x in mail_list
        ]

    def _mail_func(augmented_mail):
        _get_email = lambda x: x.split('|')[-1]

        return _get_email(list(augmented_mail.values())[-1])

    def _strip_label(dict_item, label_name):
        if label_name in dict_item:
            return dict_item[label_name]
        else:
            return False

    tocc_list = _append_label("to", to_list) + _append_label("cc", cc_list)
    deduped_list = remove_email_duplicates(tocc_list, _mail_func)

    _to_func = partial(_strip_label, label_name="to")
    _cc_func = partial(_strip_label, label_name="cc")

    to_list_final = list(filter(bool, map(_to_func, deduped_list)))
    cc_list_final = list(filter(bool, map(_cc_func, deduped_list)))

    return (to_list_final, cc_list_final)


def get_role_group_recipients(role_group_name):
    try:
        role_group = cm.RoleGroup.objects.get(role_name=role_group_name)
    except ObjectDoesNotExist:
        return []

    return [
        _x.full_name + "|" + _x.primary_email for _x in 
        role_group.contacts
    ]


def get_multi_role_group_recipients(role_groups):
    recipients = []

    for role_group in role_groups:
        recipients.extend(get_role_group_recipients(role_group))

    return recipients


def get_center_role_recipients(zone_name, center_name, role_names):
    _qs = cm.IndividualContactRoleCenter.objects.filter(
        center__center_name=center_name,
        center__zone__zone_name=zone_name,
        role__role_name__in=role_names
    )

    _qs_result = _qs.values_list('contact__first_name', 'contact__last_name', 'contact__primary_email')

    return [
        x[0] + ' ' + x[1]  + '|' + x[2] for x in _qs_result
    ]


def get_zone_role_recipients(zone_name, role_names):
    _qs = cm.IndividualContactRoleZone.objects.filter(
        zone__zone_name=zone_name,
        role__role_name__in=role_names
    )

    _qs_result = _qs.values_list('contact__first_name', 'contact__last_name', 'contact__primary_email')

    return [
        x[0] + ' ' + x[1]  + '|' + x[2] for x in _qs_result
    ]


def parse_notification_template(template):
    """
        Template looks like this:

        email:deepak@ishafoundation.org
        email:arunkumar.p@ishafoundation.org
        email:ipc.np.accounts@ishafoundation.org
        email:ipc.itsupport@ishafoundation.org
        center:Center Treasurer
        zone:RCO Accounts Incharge
        center:Sector Coordinator
        zone:Inventory
        rolegroup:Aasaan Admin
    """

    def _collate(datalist, key):
        _subdatalist = list(filter(lambda k: key == k[0], datalist))

        return tuple(_x[-1] for _x in _subdatalist)

    template_parsed = template.replace("\r\n", "\n")
    template_list = [_x.split(":") for _x in template_parsed.split("\n")]

    return {
        _x: _collate(template_list, _x) for _x in ("email", "center", "zone", "rolegroup")
    }

def get_notification_template_recipients(template, zone_name="", center_name="",
                                        supplement=[]):
    template_parsed = parse_notification_template(template)
    _center_recipients = []
    _zone_recipients = []
    _email_recipients = []
    _role_group_recipients = []

    if template_parsed["center"] and zone_name and center_name:
        _center_recipients = get_center_role_recipients(zone_name, center_name, template_parsed["center"])

    if template_parsed["zone"] and zone_name:
        _zone_recipients = get_zone_role_recipients(zone_name, template_parsed["zone"])

    if template_parsed["email"]:
        _email_recipients = list(template_parsed["email"])

    if template_parsed["rolegroup"]:
        _role_group_recipients = get_multi_role_group_recipients(template_parsed["rolegroup"])

    return remove_email_duplicates(_center_recipients + _zone_recipients + 
                                    _email_recipients + _role_group_recipients + (supplement or []))        


def get_notify_config_name(model_name, zone_name, center_name, 
                            prefix="TRIGGER", suffix="TARGET"):
    """
        Don't put underscores for prefix and suffix
        model_name ==> namespaced model name. Ex: config.models.Tag
    """
    _parse = lambda x: slugify(x).replace("-", "_").upper()

    configs = []
    
    if zone_name and center_name:
        _munge = "_".join(map(_parse, [prefix, model_name, zone_name, 
                                center_name, suffix]))
        configs.append(_munge.rstrip("_"))

    if zone_name:
        _munge = "_".join(map(_parse, [prefix, model_name, zone_name, 
                            suffix]))
        configs.append(_munge.rstrip("_"))                           

    _munge = "_".join(map(_parse, [prefix, model_name, 
                           suffix]))
    configs.append(_munge.rstrip("_"))                           
    
    return tuple(configs)


def get_zone_center(instance):
    """
        This function operates on the assumption that the 
        instance will contain attributes called zone and center
    """
    _ret = {'zone_name': '', 'center_name': ''}

    try:
        center = getattr(instance, "center")
        _ret['center_name'] = center.center_name
        _ret['zone_name'] = center.zone.zone_name
    except AttributeError:
        # no center attribute found
        try:
            zone = getattr(instance, "zone")
            _ret['zone_name'] = zone.zone_name
        except:
            # no zone found as well
            # nothing to do!
            pass

    return _ret


def get_granular_instance_config(heirarchies, configs):
    # we are assuming heirarchies are sorted with most 
    # preferring coming up first and least preferred last

    for _h in heirarchies:
        if _h in configs:
            return configs[_h]


def get_rendered_template(template_file, instance, notify_meta):
    def get_coded_content(code, template, context):
        result = ''
        for _node in template.nodelist:
            try:
                if _node.name == code:
                    _notify_meta = {**context, code: True}
                    _text = _node.render(Context(_notify_meta))
                    result = _text.replace('\n', '').replace('\t', '')
            except AttributeError:
                pass

        return result
        
    _timestamp = datetime.now().isoformat()
    with open(template_file, 'r') as template_file:
        template = template_file.read()

    _context = {
        'object': instance,
        'meta': notify_meta,
        'ts': _timestamp
    }

    t = Template(template)   
    c = Context(_context)

    subject = get_coded_content("subject", t, _context)
    frommail = get_coded_content("frommail", t, _context)

    return {
        'content': t.render(c),
        'from': frommail,
        'subject': subject
    }

    

