# -*- coding: utf-8 -*-

"""
Create ORS programs for newly defined programs in Aasaan
"""
from datetime import date

from config.joomla.joomla import JoomlaInterface

from django.core.management.base import BaseCommand
from django.conf import settings

from schedulemaster.models import ProgramSchedule
from config.models import Configuration

def get_configuration_dictionary():
    config_dict = dict()
    for configuration in Configuration.objects.all():
        if configuration.configuration_key.startswith('JOOMLA'):
            config_dict[configuration.configuration_key] = configuration.configuration_value

    return config_dict


class Command(BaseCommand):
    help = "Create Joomla programs for newly created Aasaan schedules"

    def handle(self, *args, **options):
        config_dict = get_configuration_dictionary()

        filter_programs = config_dict["JOOMLA_PROGRAM_CREATION_PROGRAM_TYPES"]
        filter_programs = [x.strip() for x in filter_programs.split("\r\n")]

        exclude_zones = config_dict["JOOMLA_PROGRAM_CREATE_EXCLUDE_ZONES"]
        exclude_zones = [x.strip() for x in exclude_zones.split("\r\n")]

        joomla = JoomlaInterface(uid=settings.JOOMLA_USER,
                                        pwd=settings.JOOMLA_PASSWORD)

        if not joomla.authenticate():
            return

        program_schedules = ProgramSchedule.objects.filter(online_registration_code="",
                                                            online_registration=True,
                                                            hidden=False,
                                                            program__admin=False,
                                                           program__name__in=filter_programs,
                                                           start_date__gte=date.today()).exclude(status='CA')

        programs_created = 0

        for each_schedule in program_schedules:
            if each_schedule.status == 'CA':
                continue

            programs_created += 1
            print(each_schedule)
            program_code = joomla.create_new_program(each_schedule, config_dict)
            print(each_schedule.id, program_code)
            each_schedule.online_registration_code = program_code
            each_schedule.save()

