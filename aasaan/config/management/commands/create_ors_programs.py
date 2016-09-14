# -*- coding: utf-8 -*-

"""
Create ORS programs for newly defined programs in Aasaan
"""
from datetime import date

from config.ors.ors import ORSInterface

from django.core.management.base import BaseCommand
from django.conf import settings

from communication.api import stage_pushover, send_communication
from schedulemaster.models import ProgramSchedule
from config.models import get_configuration

def get_configuration_dictionary():
    config_elements = ["ORS_PROGRAM_PURPOSE_CODE_7DAY",
                       "ORS_PROGRAM_CREATE_PARTICIPANT_MSG",
                       "ORS_PROGRAM_CREATE_SMS_SENDER_ID",
                       "ORS_PROGRAM_CREATE_SMS_PROFILE_ID",
                       "ORS_PROGRAM_CENTER_CODE",
                       "ORS_PROGRAM_ENTITY_7DAY",
                       "ORS_BATCH_TYPE_7DAY",
                       "ORS_PROGRAM_CODE_7DAY",
                       "ORS_COMPANY_ID_IIIS",
                       "ORS_PROGRAM_CREATION_PROGRAM_TYPES"]

    config_dict = dict(zip(config_elements, map(get_configuration, config_elements)))

    return config_dict

class Command(BaseCommand):
    help = "Create ORS programs for newly created Aasaan schedules"

    def handle(self, *args, **options):
        config_dict = get_configuration_dictionary()

        filter_programs = config_dict["ORS_PROGRAM_CREATION_PROGRAM_TYPES"]
        filter_programs = [x.strip() for x in filter_programs.split(",")]

        ors_interface = ORSInterface(settings.ORS_USER, settings.ORS_PASSWORD)
        if not ors_interface.authenticate():
            send_communication("Pushover", stage_pushover(communication_message="Unable to login to ORS. Aborting!",
                                                          role_groups = ["Aasaan Admin"]))

        program_schedules = ProgramSchedule.objects.filter(event_management_code="",
                                                           program__name__in=filter_programs,
                                                           start_date__gte=date.today())

        programs_created = 0
        for each_schedule in program_schedules:
            if each_schedule.status == 'CA':
                continue

            programs_created += 1
            program_code = ors_interface.create_new_program(each_schedule, config_dict)

            each_schedule.event_management_code = program_code
            each_schedule.save()

        send_communication("Pushover", stage_pushover(communication_message="%d ORS programs created! " % programs_created,
                                                      role_groups = ["Aasaan Admin"]))
