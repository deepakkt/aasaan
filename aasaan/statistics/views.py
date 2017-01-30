import json
from django.shortcuts import render
from django.views.generic import View
from config.models import get_configuration
from contacts.models import Zone, IndividualContactRoleZone
from statistics.models import StatisticsProgramCounts, OverseasEnrollement, UyirNokkamEnrollement, TrainingStatistics
from django.db.models import Q


class StatisticsDashboard(View):
    template = "statistics/statistics_dashboard.html"

    def get_program_counts(self):
        statistics = {}
        months = ['2016-07', '2016-08', '2016-09', '2016-10', '2016-11', '2016-12']
        months.sort()
        self.tn_statistics(statistics, months)
        self.otn_statistics(statistics, months)
        self.iyc_statistics(statistics, months)
        self.overseas_statistics(statistics, months)
        return statistics

    def tn_statistics(self, statistics, months):
        tn_zone = get_zones(get_configuration('STATISTICS_ZONE_TN'))
        ie_programs = get_configuration('STATISTICS_IE_PROGRAM').split('#')
        ie_programs = [x.strip(' ') for x in ie_programs]

        tn_ie_list = list(
            StatisticsProgramCounts.objects.filter(program_window__in=months).filter(zone_name__in=tn_zone).filter(
                program_name__in=ie_programs).order_by('zone_name', 'program_name').values_list('zone_name',
                                                                                                'program_name',
                                                                                                'program_window',
                                                                                                'participant_count',
                                                                                                'program_count'))
        monthly_list = get_monthly_list(months, tn_ie_list)

        title = ['Month']
        for zone in tn_zone:
            title.append(zone)
        title.append('Average')

        statistics['TN_IE'] = []
        statistics['TN_IE'].append(title)
        set_statistics_data(months, tn_zone, monthly_list, statistics['TN_IE'], participant_avg=0)
        statistics['TN_AVG'] = []
        statistics['TN_AVG'].append(title)
        set_statistics_data(months, tn_zone, monthly_list, statistics['TN_AVG'], participant_avg=1)
        statistics['TN_OTHER'] = []
        statistics['TN_OTHER'].append(title)

        tn_other_list = list(
            StatisticsProgramCounts.objects.filter(program_window__in=months).filter(zone_name__in=tn_zone).filter(
                ~Q(program_name__in=ie_programs)).order_by('zone_name', 'program_name').values_list('zone_name',
                                                                                                    'program_name',
                                                                                                    'program_window',
                                                                                                    'participant_count',
                                                                                                    'program_count'))
        monthly_list = get_monthly_list(months, tn_other_list)
        set_statistics_data(months, tn_zone, monthly_list, statistics['TN_OTHER'], participant_avg=0)

    def otn_statistics(self, statistics, months):

        otn_zone = get_zones(get_configuration('STATISTICS_ZONE_OTN'))
        title = ['Month']
        for zone in otn_zone:
            title.append(zone)
        title.append('Average')
        ie_programs = get_configuration('STATISTICS_IE_PROGRAM').split('#')
        ie_programs = [x.strip(' ') for x in ie_programs]
        otn_ie_list = list(
            StatisticsProgramCounts.objects.filter(program_window__in=months).filter(zone_name__in=otn_zone).filter(
                program_name__in=ie_programs).order_by('zone_name', 'program_name').values_list('zone_name',
                                                                                                'program_name',
                                                                                                'program_window',
                                                                                                'participant_count',
                                                                                                'program_count'))
        statistics['OTN_IE_PROGRAMS'] = []
        statistics['OTN_IE_PROGRAMS'].append(title)
        monthly_list = get_monthly_list(months, otn_ie_list)
        set_statistics_data(months, otn_zone, monthly_list, statistics['OTN_IE_PROGRAMS'], participant_avg=0)

        statistics['OTN_AVG'] = []
        statistics['OTN_AVG'].append(title)
        set_statistics_data(months, otn_zone, monthly_list, statistics['OTN_AVG'], participant_avg=1)

        otn_other_list = list(
            StatisticsProgramCounts.objects.filter(program_window__in=months).filter(zone_name__in=otn_zone).filter(
                ~Q(program_name__in=ie_programs)).order_by('zone_name', 'program_name').values_list('zone_name',
                                                                                                    'program_name',
                                                                                                    'program_window',
                                                                                                    'participant_count',
                                                                                                    'program_count'))
        statistics['OTN_OTHER_PROGRAMS'] = []
        statistics['OTN_OTHER_PROGRAMS'].append(title)
        monthly_list = get_monthly_list(months, otn_other_list)
        set_statistics_data(months, otn_zone, monthly_list, statistics['OTN_OTHER_PROGRAMS'], participant_avg=0)

    def iyc_statistics(self, statistics, months):
        iyc_zone = 'Isha Yoga Center'
        title = ['Month', iyc_zone, 'Average']
        ie_programs = get_configuration('STATISTICS_IE_PROGRAM').split('#')
        ie_programs = [x.strip(' ') for x in ie_programs]
        iyc_ie_list = list(
            StatisticsProgramCounts.objects.filter(program_window__in=months).filter(zone_name=iyc_zone).filter(
                program_name__in=ie_programs).order_by('zone_name', 'program_name').values_list('zone_name',
                                                                                                'program_name',
                                                                                                'program_window',
                                                                                                'participant_count',
                                                                                                'program_count'))
        statistics['IYC_IE_PROGRAMS'] = []
        statistics['IYC_IE_PROGRAMS'].append(title)
        monthly_list = get_monthly_list(months, iyc_ie_list)
        set_iyc_statistics_data(months, iyc_zone, monthly_list, statistics['IYC_IE_PROGRAMS'], participant_avg=0)
        statistics['IYC_AVG'] = []
        statistics['IYC_AVG'].append(title)
        set_iyc_statistics_data(months, iyc_zone, monthly_list, statistics['IYC_AVG'], participant_avg=1)

        iyc_other_list = list(
            StatisticsProgramCounts.objects.filter(program_window__in=months).filter(zone_name__in=iyc_zone).filter(
                ~Q(program_name__in=ie_programs)).order_by('zone_name', 'program_name').values_list('zone_name',
                                                                                                    'program_name',
                                                                                                    'program_window',
                                                                                                    'participant_count',
                                                                                                    'program_count'))
        statistics['IYC_OTHER_PROGRAMS'] = []
        statistics['IYC_OTHER_PROGRAMS'].append(title)
        monthly_list = get_monthly_list(months, iyc_other_list)
        set_iyc_statistics_data(months, iyc_zone, monthly_list, statistics['IYC_OTHER_PROGRAMS'], participant_avg=0)

    def overseas_statistics(self, statistics, months):

        overseas_zone = get_zones(get_configuration('STATISTICS_ZONE_OVS'))
        title = ['Month']
        for zone in overseas_zone:
            title.append(zone)
        title.append('Average')
        # title = ['Month', overseas_zone, 'Average']
        ie_programs = get_configuration('STATISTICS_IE_PROGRAM').split('#')
        ie_programs = [x.strip(' ') for x in ie_programs]
        ovs_ie_list = list(
            StatisticsProgramCounts.objects.filter(program_window__in=months).filter(
                zone_name__in=overseas_zone).filter(
                program_name__in=ie_programs).order_by('zone_name', 'program_name').values_list('zone_name',
                                                                                                'program_name',
                                                                                                'program_window',
                                                                                                'participant_count',
                                                                                                'program_count'))
        statistics['OVS_IE_PROGRAMS'] = []
        statistics['OVS_IE_PROGRAMS'].append(title)
        monthly_list = get_monthly_list(months, ovs_ie_list)
        set_statistics_data(months, overseas_zone, monthly_list, statistics['OVS_IE_PROGRAMS'], participant_avg=0)

        statistics['OVS_AVG'] = []
        statistics['OVS_AVG'].append(title)
        set_statistics_data(months, overseas_zone, monthly_list, statistics['OVS_AVG'], participant_avg=1)

        ovs_other_list = list(
            StatisticsProgramCounts.objects.filter(program_window__in=months).filter(
                ~Q(program_name__in=ie_programs)).order_by('zone_name', 'program_name').values_list('zone_name',
                                                                                     'program_name',
                                                                                     'program_window',
                                                                                     'participant_count',
                                                                                     'program_count'))
        statistics['OVS_OTHER_PROGRAMS'] = []
        statistics['OVS_OTHER_PROGRAMS'].append(title)
        monthly_list = get_monthly_list(months, ovs_other_list)
        set_statistics_data(months, overseas_zone, monthly_list, statistics['OVS_OTHER_PROGRAMS'], participant_avg=0)

    def get(self, request, *args, **kwargs):
        zones = Zone.objects.all()
        result_set = {'statistics': self.get_program_counts(), }
        return render(request, self.template, {'result': json.dumps(result_set)})


def set_statistics_data(months, zones, all_stats, statistics_data, participant_avg):
    monthly_dict = {}
    for month in months:
        monthly_dict[month] = [month, ]
        for zone in zones:
            try:
                monthly_dict[month].append(all_stats[month][zone][participant_avg])
            except KeyError:
                monthly_dict[month].append(0)

        monthly_dict[month].append(round(sum((monthly_dict[month][1:])) / len((monthly_dict[month][1:])), 2))
        statistics_data.append(monthly_dict[month])


def set_iyc_statistics_data(months, zones, all_stats, statistics_data, participant_avg):
    monthly_dict = {}
    for month in months:
        monthly_dict[month] = [month, ]
        try:
            monthly_dict[month].append(all_stats[month][zones][participant_avg])
        except KeyError:
            monthly_dict[month].append(0)
        monthly_dict[month].append(round(sum((monthly_dict[month][1:])) / len((monthly_dict[month][1:])), 2))
        statistics_data.append(monthly_dict[month])


def get_zones(zones):
    zone_list = zones.split('#')
    zone_list = [x.strip(' ') for x in zone_list]
    zone_list.sort()
    return zone_list


def get_monthly_list(months, stats_list):
    monthly_list = {}
    for month in months:
        monthly_list[month] = {}
    for s in stats_list:
        mn = {}
        mn[s[0]] = [s[3], s[4]]
        monthly_list[s[2]].update(mn)
    return monthly_list
