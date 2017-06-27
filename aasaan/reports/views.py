import json

from django.shortcuts import render
from django.views.generic import View
from django.db import connection

from contacts.models import Zone, IndividualContactRoleZone
from .models import IRCDashboardSectorCoordinators, \
        IRCDashboardMissingRoles, IRCDashboardProgramCounts, \
        IRCDashboardZoneSummary, IRCDashboardRoleSummary, \
        IRCDashboardCenterMap, IRCDashboardCenterMaterial
from config.models import get_configuration as get_config
from braces.views import LoginRequiredMixin
from django.views.generic import TemplateView


class IRCDashboard(LoginRequiredMixin, TemplateView):
    template = "reports/irc_dashboard.html"
    template_name = "reports/irc_dashboard.html"
    login_url = "/admin/login/?next=/"

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

    def get_item_summary(self):
        item_summary = dict()
        materials_chart_items = get_config('REPORTS_IRC_DASHBOARD_CENTER_MATERIALS_LIST')
        materials_chart_items = materials_chart_items.split('\r\n')
        materials_chart_items.insert(0, 'Center')

        item_summary['data'] = list(IRCDashboardCenterMaterial.objects.values_list(
            'zone_name', 'center_name', 'item_name', 'quantity'
        ))

        item_summary['columns'] = tuple(materials_chart_items)

        return item_summary

    def get(self, request, *args, **kwargs):
        zones = Zone.objects.all()

        result_set = {'sector_coordinators': self.get_sector_coordinators(),
                      'missing_roles': self.get_missing_roles(),
                      'program_counts': self.get_program_counts(),
                      'teachers': self.get_teachers(),
                      'zone_summary': self.get_zone_summary(),
                      'role_summary': self.get_role_summary(),
                      'center_map': self.get_center_map(),
                      'item_summary': self.get_item_summary()}

        return render(request, self.template, {'zones': zones,
                                               'result': json.dumps(result_set).replace("'", "\\u0027")})
