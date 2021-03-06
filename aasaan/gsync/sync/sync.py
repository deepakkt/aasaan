"""
This is an older version of sync.
This is kept for legacy reasons. All sync requirements
should be addressed with the new sync module.
"""
from datetime import datetime

from schedulemaster.models import ProgramSchedule
from contacts.models import IndividualContactRoleCenter, IndividualContactRoleZone

from .api import open_workbook, delete_worksheets, update_header_row, \
    update_cell, update_row, authenticate

from .settings import schedule_sync_rows, contact_sync_rows, CONTACTS_SHEEET_KEY, \
    schedule_header, contact_header

from . import schedule_sync, contacts_sync

gc = authenticate()


def sync_schedules():
    global gc
    # get an instance for schedule workbook and clear all sheets
    schedule_workbook = open_workbook(gc_interface=gc)
    delete_worksheets(schedule_workbook)

    # zone map will maintain each sheet's instance along with last updated row
    zone_map = dict()

    # get all schedules sorted by zone, start date and center name
    schedules = ProgramSchedule.objects.all().order_by('center__zone', 'program', '-start_date', 'center')

    for each_schedule in schedules:
        current_zone = each_schedule.center.zone.zone_name

        # add a new mapping if this zone hasn't appeared before
        if not zone_map.get(current_zone):
            zone_map[current_zone] = [2, schedule_workbook.add_worksheet(current_zone, 1000, 26)]
            update_header_row(zone_map[current_zone][-1], values_list=schedule_sync_rows)

        # generate program timings in the format of M-N-E
        timing_codes = '-'.join([x.batch.batch_code for x in each_schedule.programbatch_set.all()])

        # get all venues for this program
        schedule_venue = each_schedule.programvenueaddress_set.all()

        # build a value list
        schedule_values = [zone_map[current_zone][0] - 1,
                           current_zone,
                           each_schedule.start_date.isoformat(),
                           each_schedule.end_date.isoformat(),
                           each_schedule.center.center_name,
                           each_schedule.program.name,
                           timing_codes,
                           each_schedule.contact_phone1,
                           each_schedule.contact_email,
                           "" if not schedule_venue else schedule_venue[0].address]

        current_schedule = schedule_header(*schedule_values)

        for schedule_filter in schedule_sync.ScheduleSync.filters:
            current_schedule = schedule_filter.filter_row(current_schedule, each_schedule)

        update_row(zone_map[current_zone][-1], start_row=zone_map[current_zone][0],
                   start_col=1,
                   values_list=tuple(current_schedule))

        zone_map[current_zone][0] += 1

    last_synced = 'Last synced: ' + datetime.now().isoformat()
    update_cell(schedule_workbook.worksheet("Reference"), "A1", last_synced)


def sync_contacts():
    global gc
    contacts_workbook = open_workbook(spreadsheet_key=CONTACTS_SHEEET_KEY,
                                      gc_interface=gc)

    delete_worksheets(contacts_workbook)

    # zone map will maintain each sheet's instance along with last updated row
    zone_map = dict()

    # get all schedules sorted by zone, start date and center name
    contacts_zone = IndividualContactRoleZone.objects.all().order_by('zone', 'role',
                                                                     'contact__first_name')
    contacts_center = IndividualContactRoleCenter.objects.all().order_by('center__zone', 'center',
                                                                         'role',
                                                                         'contact__first_name')

    for each_contact in contacts_zone:
        current_zone = each_contact.zone.zone_name

        if not zone_map.get(current_zone):
            zone_map[current_zone] = [2, contacts_workbook.add_worksheet(current_zone, 1000, 26)]
            update_header_row(zone_map[current_zone][-1], values_list=contact_sync_rows)

        # get addresses for this contact
        contact_address = each_contact.contact.contactaddress_set.all()

        contact_values = [zone_map[current_zone][0] - 1,
                          each_contact.contact.full_name,
                          each_contact.contact.primary_mobile,
                          each_contact.contact.whatsapp_number,
                          each_contact.contact.primary_email,
                          'Zone',
                          current_zone,
                          each_contact.role.role_name,
                          "" if not contact_address else contact_address[0].address]

        current_contact = contact_header(*contact_values)

        for contact_filter in contacts_sync.ContactSync.filters:
            current_contact = contact_filter.filter_row(current_contact, each_contact)

        update_row(zone_map[current_zone][-1], start_row=zone_map[current_zone][0],
                   start_col=1,
                   values_list=tuple(current_contact))

        zone_map[current_zone][0] += 1

    for each_contact in contacts_center:
        current_zone = each_contact.center.zone.zone_name

        if not zone_map.get(current_zone):
            zone_map[current_zone] = [2, contacts_workbook.add_worksheet(current_zone, 1000, 26)]
            update_header_row(zone_map[current_zone][-1], values_list=contact_sync_rows)

        contact_values = [zone_map[current_zone][0] - 1,
                          each_contact.contact.full_name,
                          each_contact.contact.primary_mobile,
                          each_contact.contact.whatsapp_number,
                          each_contact.contact.primary_email,
                          'Center',
                          each_contact.center.center_name,
                          each_contact.role.role_name]

        update_row(zone_map[current_zone][-1], start_row=zone_map[current_zone][0],
                   start_col=1,
                   values_list=contact_values)

        zone_map[current_zone][0] += 1

    last_synced = 'Last synced: ' + datetime.now().isoformat()
    update_cell(contacts_workbook.worksheet("Reference"), "A1", last_synced)


def sync_all():
    #sync_contacts()
    sync_schedules()