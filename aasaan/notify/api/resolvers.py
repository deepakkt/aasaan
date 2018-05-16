from pprint import pprint
from functools import partial

from django.forms.models import model_to_dict

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
        return '|'.join(_fnln, _email)

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