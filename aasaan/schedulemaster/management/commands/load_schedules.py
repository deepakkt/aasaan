# -*- coding: utf-8 -*-

"""
Sync schedules to google sheet
All definitions are given in gsync.settings
"""

import csv
from collections import Counter
from datetime import date

from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist

from schedulemaster.models import ProgramSchedule, ProgramScheduleCounts, ProgramCountMaster, \
    ProgramMaster, LanguageMaster
from contacts.models import Center


def return_count_master(category):
    return ProgramCountMaster.objects.get(count_category=category.strip())


def get_center(center, zone):
    return Center.objects.get(center_name=center.strip(),
                              zone__zone_name=zone.strip())


def get_program(program):
    return ProgramMaster.objects.get(name=program.strip())


def get_date(ddmmyyyy):
    try:
        d, m, y = map(int, ddmmyyyy.split('-'))
        return date(y, m, d)
    except ValueError:
        y, m, d = map(int, ddmmyyyy.split('-'))
        return date(y, m, d)


def get_or_set_count(program, category, value):
    if not value:
        return

    current_count = ProgramScheduleCounts.objects.filter(program=program,
                                                         category=category)

    if not current_count:
        new_count = ProgramScheduleCounts()
        new_count.program = program
        new_count.category = category
        new_count.value = int(value)
        new_count.save()
        return new_count
    else:
        current_count = current_count[0]
        current_count.value = int(value)
        current_count.save()
        return current_count


class Command(BaseCommand):
    help = "Sync schedules. See gsync.settings for definitions"

    def add_arguments(self, parser):
        parser.add_argument('schedule_file', nargs='+', type=str)

    def handle(self, *args, **options):
        for each_file in options['schedule_file']:
            load_file = each_file
            break

        row_headers = "sno,status,start,end,zone,center,program,donation,gender,language,total,m,n,e,a,i".split(",")

        schedule_reader = csv.reader(open(load_file))

        counts = Counter()

        morning, noon, evening, total, absentees, volunteers = map(return_count_master,
                                                                   ['Morning', 'Noon',
                                                                    'Evening',
                                                                    'Total Participant Count',
                                                                    'Absentees',
                                                                    'Initiation Volunteers Count'])

        for each_row in schedule_reader:
            if schedule_reader.line_num == 1:
                # bypass header row
                continue

            counts['processed'] += 1

            current_row = dict(zip(row_headers, each_row))

            if current_row['status'].lower() == 'do not load':
                counts['skipped'] += 1
                self.stdout.write("%d ==> Skipping %s" % (schedule_reader.line_num, each_row))
                continue

            try:
                match_schedule = ProgramSchedule.objects.filter(program=get_program(current_row['program']),
                                                                center=get_center(current_row['center'],
                                                                                  current_row['zone']),
                                                                start_date=get_date(current_row['start']))

                if not match_schedule:
                    new_schedule = ProgramSchedule()
                else:
                    new_schedule = match_schedule[0]

                new_schedule.program = get_program(current_row['program'])
                new_schedule.center = get_center(current_row['center'], current_row['zone'])
                new_schedule.start_date = get_date(current_row['start'])
                new_schedule.end_date = get_date(current_row['end'])
                new_schedule.gender = {'Ladies': 'F',
                                       'Gents': 'M',
                                       'All': 'BO'}.get(current_row['gender'].strip()) or 'BO'

                new_schedule.primary_language = LanguageMaster.objects.get(name=current_row['language'].strip())

                new_schedule.donation_amount = int(current_row['donation'])
                new_schedule.status = 'RC'
                new_schedule.contact_name = 'System Loaded'
                new_schedule.contact_email = 'aasaanbot@aasaan.isha.in'
                new_schedule.contact_phone1 = '9489045110'

                new_schedule.save()

                self.stdout.write("%d ==> Updated %s with id %d" % (schedule_reader.line_num, each_row,
                                                                  new_schedule.id))

                get_or_set_count(new_schedule, morning, current_row['m'])
                get_or_set_count(new_schedule, evening, current_row['e'])
                get_or_set_count(new_schedule, noon, current_row['n'])
                get_or_set_count(new_schedule, total, current_row['total'])
                get_or_set_count(new_schedule, absentees, current_row.get('a'))
                get_or_set_count(new_schedule, volunteers, current_row.get('i'))

                if not match_schedule:
                    counts['added'] += 1
                else:
                    counts['updated'] += 1

            except:
                counts['aborted'] += 1
                self.stdout.write("%d ==> Aborted %s. Check data" % (schedule_reader.line_num, each_row))

        self.stdout.write('Processed => %d' % counts['processed'])
        self.stdout.write('Skipped => %d' % counts['skipped'])
        self.stdout.write('Newly added => %d' % counts['added'])
        self.stdout.write('Aborted => %d' % counts['aborted'])
        self.stdout.write('Updated => %d' % counts['updated'])
