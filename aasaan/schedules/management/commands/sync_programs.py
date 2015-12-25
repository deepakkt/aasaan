from schedules.management.commands import _ors_sync
from django.core.management.base import BaseCommand
from contacts.models import Center
from schedules.models import Schedule, SyncLog

from datetime import datetime


def match_center(program_center, master_center):
    program_center_clean = program_center.replace("-", " ")
    program_center_clean = program_center_clean.replace(",", " ")

    master_center_clean = master_center.replace("-", " ")
    master_center_clean = master_center_clean.replace(",", " ")

    program_center_set = set(program_center_clean.lower().strip())
    master_center_set = set(master_center_clean.lower().strip())

    common_letters = program_center_set.intersection(master_center_set)

    length_confidence = (len(program_center_clean) if len(program_center_clean) < len(master_center_clean)
                         else len(master_center_clean)) / \
                        (len(program_center_clean) if len(program_center_clean) > len(master_center_clean)
                         else len(master_center_clean)) * 100

    first_match_confidence = int(len(common_letters) / len(program_center_set) * 100)
    second_match_confidence = int(len(common_letters) / len(master_center_set) * 100)

    net_confidence = int((first_match_confidence + second_match_confidence + length_confidence) / 3)

    return net_confidence


def save_program(program, assigned_center, matched, confidence, approved='N'):
    new_program = Schedule()

    new_program.program_title = program['ProgramName']
    new_program.program_code = program['ProgramID']
    new_program.program_code_source = 'ORS'
    new_program.program_type = program['ProgramCode']
    new_program.start_date = program['StartDate']
    new_program.center = assigned_center
    new_program.matched = matched
    new_program.match_confidence = confidence
    new_program.match_overridden = 'N'
    new_program.match_approved = approved

    new_program.remarks = "\n".join([datetime.now().isoformat(),
                                     "System assigned %s at %d percent confidence" % (assigned_center.center_name,
                                                                                      confidence)])

    new_program.save()


def sync_main():
    # check if schedule table is already populated (1 record at least). If so, we
    # will do an incremental refresh. Else we have to do a full scan
    filter_on_date = True if Schedule.objects.count() > 0 else False
    program_list = _ors_sync.ors_get_program_list(_ors_sync.ors_authenticate(),
                                                  program_filter='IYP',
                                                  date_filter=filter_on_date)

    num_records_fetched = len(program_list)
    num_records_skipped = 0
    num_records_matched = 0

    for each_program in program_list:
        existing_program = Schedule.objects.filter(program_code=each_program['ProgramID'])
        if len(existing_program) > 0:
            num_records_skipped += 1
            continue

        contact_centers = Center.objects.filter(center_name=each_program['Center'])

        if len(contact_centers) >= 1:
            save_program(each_program, contact_centers[0], matched='Y', confidence=100,
                         approved='Y')
            num_records_matched += 1
            continue

        # at this point, no definitive match is present, so we have to do heuristic
        matches = {this_center.center_name: match_center(each_program['Center'], this_center.center_name)
                   for this_center in Center.objects.all()}

        maximum_confidence = max(matches.values())
        maximum_confidence_center_name = list(matches.keys())[list(matches.values()).index(maximum_confidence)]
        maximum_confidence_center = Center.objects.filter(center_name=maximum_confidence_center_name)[0]

        if maximum_confidence >= 80:
            match_successful = 'Y'
            num_records_matched += 1
        else:
            match_successful = 'N'

        if maximum_confidence >= 95:
            approve_match = 'Y'
        else:
            approve_match = 'N'

        save_program(each_program, maximum_confidence_center, match_successful,
                     maximum_confidence, approve_match)

    sync_entry = SyncLog()
    sync_entry.records_fetched = num_records_fetched
    sync_entry.new_records_added = num_records_fetched - num_records_skipped
    sync_entry.old_records_skipped = num_records_skipped
    sync_entry.matched_centers = num_records_matched
    sync_entry.save()


class Command(BaseCommand):
    help = 'Sync schedules from ORS'

    def handle(self, *args, **options):
        sync_main()
        last_sync = SyncLog.objects.all()[0]
        self.stdout.write('%s' % (last_sync))
