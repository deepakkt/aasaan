import json

from django.shortcuts import render
from django.views.generic import View
from django.db import connection
from config.models import get_configuration

from contacts.models import Zone, IndividualContactRoleZone
from .models import StatisticsProgramCounts
from django.db.models import Q
# Create your views here.


class StatisticsDashboard(View):

    template = "statistics/statistics_dashboard.html"

    def get_program_counts(self):
        statistics = {}
        months = ['2016-07', '2016-08', '2016-09', '2016-10', '2016-11', '2016-12']
        months.sort()
        self.tn_statistics(statistics, months)
        self.otn_statistics(statistics, months)
        return statistics

    def tn_statistics(self, statistics, months):
        stats = dict()
        tn_zone = get_configuration('STATISTICS_ZONE_TN').split(',')
        ie_programs = get_configuration('STATISTICS_IE_PROGRAM').split(',')
        ie_programs = [x.strip(' ') for x in ie_programs]
        tn_zone = [x.strip(' ') for x in tn_zone]
        tn_zone.sort()
        stats['IE_PROGRAMS'] = list(StatisticsProgramCounts.objects.filter(program_window__in=months).filter(zone_name__in=tn_zone).filter(program_name__in=ie_programs).order_by('zone_name', 'program_name').values_list('zone_name', 'program_name', 'program_window', 'participant_count', 'program_count'))
        stats['OTHER_PROGRAMS'] = list(StatisticsProgramCounts.objects.filter(program_window__in=months).filter(zone_name__in=tn_zone).filter(~Q(program_name__in=ie_programs)).order_by('zone_name', 'program_name').values_list('zone_name', 'program_name', 'program_window', 'participant_count', 'program_count'))
        all_stats = {}
        tn_zone = get_configuration('STATISTICS_ZONE_TN').split(',')
        # otn_zone = get_configuration('STATISTICS_ZONE_OTN').split(',')
        tn_zone = [x.strip(' ') for x in tn_zone]
        tn_zone.sort()
        for month in months:
            all_stats[month] = {}
        for s in stats['IE_PROGRAMS']:
            mn = {}
            mn[s[0]] = [s[3], s[4]]
            all_stats[s[2]].update(mn)
        title = ['Month']
        for zone in tn_zone:
            title.append(zone)
        title.append('Average')

        statistics['TN_IE'] = []
        statistics['TN_IE'].append(title)
        self.set_statistics_data(months, tn_zone, all_stats, statistics['TN_IE'], participant_avg=0)
        statistics['TN_AVG'] = []
        statistics['TN_AVG'].append(title)
        self.set_statistics_data(months, tn_zone, all_stats, statistics['TN_AVG'], participant_avg=1)
        statistics['TN_OTHER'] = []
        statistics['TN_OTHER'].append(title)
        all_stats = {}
        for month in months:
            all_stats[month] = {}
        for s in stats['OTHER_PROGRAMS']:
            mn = {}
            mn[s[0]] = [s[3], s[4]]
            all_stats[s[2]].update(mn)
        self.set_statistics_data(months, tn_zone, all_stats, statistics['TN_OTHER'], participant_avg=0)

    def otn_statistics(self, statistics, months):
        months = ['2016-07', '2016-08', '2016-09', '2016-10', '2016-11', '2016-12']
        months.sort()
        otn_zone = get_configuration('STATISTICS_ZONE_OTN').split('-')
        otn_zone = [x.strip(' ') for x in otn_zone]
        otn_zone.sort()
        title = ['Month']
        for zone in otn_zone:
            title.append(zone)
        title.append('Average')
        stats = dict()
        ie_programs = get_configuration('STATISTICS_IE_PROGRAM').split(',')
        ie_programs = [x.strip(' ') for x in ie_programs]
        stats['OTN_IE_PROGRAMS'] = list(StatisticsProgramCounts.objects.filter(program_window__in=months).filter(zone_name__in=otn_zone).filter(program_name__in=ie_programs).order_by('zone_name', 'program_name').values_list('zone_name', 'program_name', 'program_window', 'participant_count', 'program_count'))
        statistics['OTN_IE_PROGRAMS'] = []
        statistics['OTN_IE_PROGRAMS'].append(title)
        all_stats = {}
        for month in months:
            all_stats[month] = {}
        for s in stats['OTN_IE_PROGRAMS']:
            mn = {}
            mn[s[0]] = [s[3], s[4]]
            all_stats[s[2]].update(mn)
        self.set_statistics_data(months, otn_zone, all_stats, statistics['OTN_IE_PROGRAMS'], participant_avg=0)

        statistics['OTN_AVG'] = []
        statistics['OTN_AVG'].append(title)
        self.set_statistics_data(months, otn_zone, all_stats, statistics['OTN_AVG'], participant_avg=1)

        stats['OTN_OTHER_PROGRAMS'] = list(StatisticsProgramCounts.objects.filter(program_window__in=months).filter(zone_name__in=otn_zone).filter(~Q(program_name__in=ie_programs)).order_by('zone_name', 'program_name').values_list('zone_name', 'program_name', 'program_window', 'participant_count', 'program_count'))
        statistics['OTN_OTHER_PROGRAMS'] = []
        statistics['OTN_OTHER_PROGRAMS'].append(title)
        all_stats = {}
        for month in months:
            all_stats[month] = {}
        for s in stats['OTN_OTHER_PROGRAMS']:
            mn = {}
            mn[s[0]] = [s[3], s[4]]
            all_stats[s[2]].update(mn)
        self.set_statistics_data(months, otn_zone, all_stats, statistics['OTN_OTHER_PROGRAMS'], participant_avg=0)

    def set_statistics_data(self, months, zones, all_stats, statistics_data, participant_avg):
        monthly_dict = {}
        for month in months:
           monthly_dict[month] = [month, ]
           for zone in zones:
               try:
                   monthly_dict[month].append(all_stats[month][zone][participant_avg])
               except KeyError:
                   monthly_dict[month].append(0)
           monthly_dict[month].append(round(sum((monthly_dict[month][1:]))/len((monthly_dict[month][1:])),2))
           statistics_data.append(monthly_dict[month])

    def get_zone(self):

        return

    def get(self, request, *args, **kwargs):
        zones = Zone.objects.all()
        result_set = {'statistics': self.get_program_counts(), }
        return render(request, self.template, {'result': json.dumps(result_set)})

