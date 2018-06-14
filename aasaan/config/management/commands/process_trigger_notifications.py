# -*- coding: utf-8 -*-
from os.path import join
from datetime import datetime
from pathlib import Path
from datetime import datetime
import json

from django.core.management.base import BaseCommand
from django.conf import settings

from django_rq import enqueue

from notify.models import Notifier

from notify.api.sendgrid_api import send_email
from notify.api.resolvers import get_notify_config_name, get_zone_center, \
                                    get_notify_config_name, \
                                    get_notification_template_recipients, \
                                    get_rendered_template, \
                                    get_granular_instance_config

from notify.api.sendgrid_api import stage_classic_notification                                    

from config.config_utils import rq_present
from config.apps import get_notify_template_dict, get_notify_properties
from config.models import get_configurations
from config.config_utils import rq_present


def process_instance_trigger(_instance, _model_setting, 
                            trigger_configs, template_path):
    _model = tuple(_model_setting)[0]
    _model_reference = _model_setting[_model][0]
    _model_notify = get_notify_properties(_model_reference)
    _create_template = join(template_path, _model_setting[_model][1])
    _modify_template = join(template_path, _model_setting[_model][2])

    zone_center = get_zone_center(_instance)

    instance_configs = get_notify_config_name(_model, **zone_center)
    valid_configs = tuple(set.intersection(set(instance_configs), set(tuple(trigger_configs))))
    instance_configs = [x for x in instance_configs if x in valid_configs]

    if not instance_configs:
        print('No valid usable configurations found for "%s" instance "%s". Skipping...' % (_model, _instance))
        return False

    targets_template = get_granular_instance_config(instance_configs, trigger_configs)
    _supplementary = _model_notify["notify_recipients"] and _model_reference.NotifyMeta.get_recipients(_instance) 
    _attachments = (_model_notify["notify_attachments"] and _model_reference.NotifyMeta.get_attachments(_instance)) or []

    template_recipients = get_notification_template_recipients(targets_template, 
                                                                **zone_center,
                                                                supplement=_supplementary)

    if not template_recipients:
        print('All seemed well so far. But not recipients found for "%s" instance "%s". Skipping...' % (_model, _instance))
        return False

    notify_meta = json.loads(_instance.notify_meta)

    if notify_meta.get('created', ''):
        _template = _create_template
    else:
        _template = _modify_template

    # augment notify metadata with zone and center info
    notify_meta = {**notify_meta, **zone_center}

    # get template and subject
    email_content = get_rendered_template(_template, _instance, notify_meta)
    email_message = email_content.get("content")
    email_subject = email_content.get("subject")
    email_from = email_content.get("from")

    stage_classic_notification("Trigger Notification", email_from,
                                template_recipients, list(), email_subject,
                                email_message, _attachments,
                                sender_in_cc=False)

    _instance.notify_meta = ""                                            
    _instance.notify_toggle = False
    _instance.save()
    return True


class Command(BaseCommand):
    help = "Send all communications under 'scheduled'"

    def handle(self, *args, **options):
        root_path = settings.BASE_DIR
        template_path = join(root_path, "templates", "mail_templates", "trigger_notifications")
        trigger_configs = get_configurations('TRIGGER')

        notify_models = get_notify_template_dict()

        for _model_setting in notify_models:
            _model = tuple(_model_setting)[0]
            print("Processing triggers for ", _model)

            _model_reference = _model_setting[_model][0]
            _model_notify = get_notify_properties(_model_reference)
            _create_template = join(template_path, _model_setting[_model][1])
            _modify_template = join(template_path, _model_setting[_model][2])

            if not Path(_modify_template).is_file():
                print("Email template for modify not found. Skipping")
                continue

            if _model_notify["notify_creation"] and not Path(_create_template).is_file():
                print("Email template for create not found. Skipping")
                continue

            for _instance in _model_reference.objects.filter(notify_toggle=True):
                print(_instance)

                if rq_present():
                    enqueue(process_instance_trigger, _instance=_instance,
                            _model_setting=_model_setting,
                            trigger_configs=trigger_configs,
                            template_path=template_path)
                    print("queued ", _instance, " for processing")
                else:
                    process_instance_trigger(_instance, _model_setting,
                                            trigger_configs, template_path)
                    print("processed ", _instance)