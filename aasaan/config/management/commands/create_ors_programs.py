# -*- coding: utf-8 -*-

"""
Create ORS programs for newly defined programs in Aasaan
"""
from datetime import date

from config.ors.ors import ORSInterface

from django.core.management.base import BaseCommand
from django.conf import settings

from communication.api import stage_pushover, send_communication
from schedulemaster.models import ProgramSchedule, ProgramAdditionalInformation
from config.models import Configuration


def get_configuration_dictionary():
    config_dict = dict()
    for configuration in Configuration.objects.all():
        if configuration.configuration_key.startswith('ORS'):
            config_dict[configuration.configuration_key] = configuration.configuration_value

    return config_dict


class Command(BaseCommand):
    help = "Create ORS programs for newly created Aasaan schedules"

    def handle(self, *args, **options):
        config_dict = get_configuration_dictionary()

        filter_programs = config_dict["ORS_PROGRAM_CREATION_PROGRAM_TYPES"]
        filter_programs = [x.strip() for x in filter_programs.split("\r\n")]

        exclude_zones = config_dict["ORS_PROGRAM_CREATE_EXCLUDE_ZONES"]
        exclude_zones = [x.strip() for x in exclude_zones.split("\r\n")]

        ors_interface = ORSInterface(settings.ORS_USER, settings.ORS_PASSWORD)
        if not ors_interface.authenticate():
            send_communication("Pushover", stage_pushover(communication_message="Unable to login to ORS. Aborting!",
                                                          role_groups = ["Aasaan Admin"]))
            return

        program_schedules = ProgramSchedule.objects.filter(event_management_code="",
                                                           program__name__in=filter_programs,
                                                           start_date__gte=date.today())

        programs_created = 0

        for each_schedule in program_schedules:
            if each_schedule.status == 'CA':
                continue

            if each_schedule.center.zone.zone_name in exclude_zones:
                continue

            print(each_schedule)

            programs_created += 1
            program_code = ors_interface.create_new_program(each_schedule, config_dict)
            print(program_code)

            each_schedule.event_management_code = program_code.get('code', "E9999999")
            each_schedule.save()

            ors_note = ProgramAdditionalInformation()
            ors_note.program = each_schedule
            ors_note.key = "ORS_DISPLAY_NAME"
            ors_note.value = program_code.get("display")
            ors_note.save()

        send_communication("Pushover", stage_pushover(communication_message="%d ORS programs created! " % programs_created,
                                                      role_groups = ["Aasaan Admin"]))
