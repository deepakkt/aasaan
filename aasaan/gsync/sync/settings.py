from collections import namedtuple
from django.utils.text import slugify

SCHEDULE_SHEET_KEY = "12Zj8m8eHsiYLdX-EHUY_7jSOHupPjfqWWg225zaiOVI"
SCHEDULE_SHEET_KEY_TEST = "1VeqAeWZHzy_hSesxZdu-3K2MjciEY0NUMl5rKGRD7N8"

CONTACTS_SHEET_KEY = "1n5Iy-ewKheuX40T3UJZ1I0tYjhcm7n9w2vy-65m68GY"
CONTACTS_SHEET_KEY_TEST = "1MvXoYjuZr95PAGcrm0-YTrGG7cmaJVWCxQc5r5tCfLQ"

DEFAULT_SHEET_KEY = SCHEDULE_SHEET_KEY_TEST

GDOC_ACCESS_SCOPE = ['https://spreadsheets.google.com/feeds']

schedule_sync_rows = ['SNo',
                      'Zone',
                      'Start Date',
                      'End Date',
                      'Place',
                      'Program Type',
                      'Timing',
                      'Gender',
                      'Language',
                      'Status',
                      'Contact No',
                      'Contact Email',
                      'Venue']

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