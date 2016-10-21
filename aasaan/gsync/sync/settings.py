from collections import namedtuple
from django.utils.text import slugify

from schedulemaster.models import ProgramCountMaster
from config.models import get_configuration

SCHEDULE_SHEET_KEY = "12Zj8m8eHsiYLdX-EHUY_7jSOHupPjfqWWg225zaiOVI"
SCHEDULE_SHEET_KEY_TEST = "1BegkkqiaA8TqCQLd2RJkKLLbmmdvFLJ14XkpweEgl28"

CONTACTS_SHEET_KEY = "1n5Iy-ewKheuX40T3UJZ1I0tYjhcm7n9w2vy-65m68GY"
CONTACTS_SHEET_KEY_TEST = "1MvXoYjuZr95PAGcrm0-YTrGG7cmaJVWCxQc5r5tCfLQ"

SCHEDULE_ENROLLMENT_SHEET_KEY = "1tCKRRU0OV_MXo8h3k6kNX8YXbOlDwLsjA_jW_iWoOvk"

SCHEDULE_IYC_SHEET_KEY = "1iVexEphaCV6VmBGD1gidTdOfBRmgsxKmyuqC8Lp1Tsg"

SIY_DEC_2016_SHEET_KEY = "1IEisF5tpaLZXmGxSvUY-h0M8bIGO14uV7OCqYrLHsKg"

DEFAULT_SHEET_KEY = SCHEDULE_SHEET_KEY_TEST

GDOC_ACCESS_SCOPE = ['https://spreadsheets.google.com/feeds']

schedule_sync_rows = ['SNo',
                      'Zone',
                      'Start Date',
                      'End Date',
                      'Place',
                      'Parent Center',
                      'Program Type',
                      'Timing',
                      'Gender',
                      'Language',
                      'Status',
                      'ORS Code',
                      'Joomla Code',
                      'Contact No',
                      'Contact Email',
                      'Venue',
                      'ID',
                      'Last Modified']

schedule_header = namedtuple('Schedule', [slugify(x).replace("-", "_") for x in schedule_sync_rows])

DEFAULT_SYNC_ROWS = schedule_sync_rows

contact_sync_rows = ['SNo',
                   'Name',
                   'Mobile',
                    'Whatsapp',
                   'Email',
                   'Zone',
                   'Center',
                   'Role',
                    'Address']

contact_header = namedtuple('Contact', [slugify(x).replace("-", "_") for x in contact_sync_rows])

enrollment_count_categories = get_configuration("SYNC_ENROLLMENT_COUNT_CATEGORIES").split('\r\n')

schedule_enrollment_sync_rows = ['SNo',
                                 'Zone',
                                 'Start Date',
                                 'End Date',
                                 'Place',
                                 'Parent Center',
                                 'Program Type',
                                 'Timing',
                                 'Gender',
                                 'Language',
                                 'Status',
                                 'ORS Code',
                                 'Teacher']

schedule_enrollment_sync_rows.extend(enrollment_count_categories)
schedule_enrollment_sync_rows.extend(['ID', 'Last Modified'])

schedule_enrollment_header = namedtuple('ScheduleEnrollment', [slugify(x).replace("-", "_")
                                                               for x in schedule_enrollment_sync_rows])

siy_dec2016_sync_rows = ['SNo', 'ORS Code', 'Venue', 'Enrollment']

siy_dec_2016_header = namedtuple('SIYDec2016', [slugify(x).replace("-", "_") for x in siy_dec2016_sync_rows])
