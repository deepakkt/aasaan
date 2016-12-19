import json

from django.shortcuts import render
from django.views.generic import View
from django.db import connection

from contacts.models import Zone, IndividualContactRoleZone
from .models import IRCDashboardSectorCoordinators, \
        IRCDashboardMissingRoles, IRCDashboardProgramCounts, \
        IRCDashboardZoneSummary, IRCDashboardRoleSummary, \
        IRCDashboardCenterMap

# Create your views here.

class IRCDashboard(View):
    template = "reports/irc_dashboard.html"

    def get_sector_coordinators(self):
        sector_coordinators = dict()

        sector_coordinators['data'] = list(IRCDashboardSectorCoordinators.objects.values_list(
            'zone_name', 'full_name', 'centers'
        ))

        sector_coordinators['columns'] = ('zone_name', 'full_name', 'centers')

        return sector_coordinators

    def get_missing_roles(self):
        missing_roles = dict()

        missing_roles['data'] = list(IRCDashboardMissingRoles.objects.values_list(
            'zone_name', 'center_name', 'available_roles', 'missing_roles'
        ))

        missing_roles['columns'] = ('zone_name', 'center_name', 'available_roles', 'missing_roles')

        return missing_roles

    def get_program_counts(self):
        program_counts = dict()

        program_counts['data'] = list(IRCDashboardProgramCounts.objects.order_by('program_window', 'zone_name', 'program_name').values_list(
            'zone_name', 'program_name', 'program_count', 'program_window'
        ))

        program_counts['columns'] = ('zone_name', 'program_name', 'program_count', 'program_window')

        return program_counts

    def get_zone_summary(self):
        zone_summary = dict()

        zone_summary['data'] = list(IRCDashboardZoneSummary.objects.order_by('zone_name').values_list(
            'zone_name', 'center_count', 'teacher_count', 'program_count'
        ))

        zone_summary['columns'] = ('zone_name', 'center_count', 'teacher_count', 'program_count')

        return zone_summary

    def get_role_summary(self):
        role_summary = dict()

        role_summary['data'] = list(IRCDashboardRoleSummary.objects.values_list(
            'zone_name', 'role_name', 'role_count'
        ))

        role_summary['columns'] = ('zone_name', 'role_name', 'role_count')

        return role_summary

    def get_teachers(self):
        teachers = list(IndividualContactRoleZone.objects.filter(role__role_name="Teacher").values_list(
            'zone__zone_name', 'contact__first_name', 'contact__last_name'
        ))

        teachers = [(x[0], x[1].title() + ' ' + x[2].title()) for x in teachers]
        return tuple(teachers)

    def get_center_map(self):
        center_map = dict()

        center_map['data'] = list(IRCDashboardCenterMap.objects.all().values_list(
            'zone_name', 'center_name', 'latitude', 'longitude', 'recent_program_count'
        ))

        center_map['columns'] = ('zone_name', 'center_name', 'latitude', 'longitude', 'recent_program_count')

        return center_map

    def get(self, request, *args, **kwargs):
        zones = Zone.objects.all()
        result_set = {'sector_coordinators': self.get_sector_coordinators(),
                      'missing_roles': self.get_missing_roles(),
                      'program_counts': self.get_program_counts(),
                      'teachers': self.get_teachers(),
                      'zone_summary': self.get_zone_summary(),
                      'role_summary': self.get_role_summary(),
                      'center_map': self.get_center_map()}
        return render(request, self.template, {'zones': zones,
                                               'result': json.dumps(result_set).replace("'", "\\u0027")})
