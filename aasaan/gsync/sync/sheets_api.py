import gspread
from oauth2client.client import SignedJwtAssertionCredentials

from django.core.exceptions import ImproperlyConfigured

from aasaan.settings.config import gdoc_key

from .settings import DEFAULT_SHEET_KEY, \
    GDOC_ACCESS_SCOPE, \
    DEFAULT_SYNC_ROWS


def getcolumnnumber(colname="A"):
    # We can hard code 26, but fixing it here might
    # make it easier to port this function later
    base=26

    # Creates a dictionary that maps characters to their column number values
    # Example, "A" maps to 1
    charmap = dict([(chr(x), x-64) for x in range(65, 65+base)])

    # Capitalize and convert the column names to a list
    # we reverse it to take advantage of default python ordinal positions
    # as we will see in a bit
    collist = list(colname.upper())
    collist.reverse()

    exponents = list(enumerate(collist))

    return sum([charmap[y] * (base ** x) for (x, y) in exponents])


def getcolumn(colnum=1):
    base = 26
    cellmap = {1: 'A',  2: 'B',  3: 'C',  4: 'D',  5: 'E',  6: 'F',
               7: 'G',  8: 'H',  9: 'I',  10: 'J',  11: 'K',  12: 'L',
               13: 'M',  14: 'N',  15: 'O',  16: 'P',  17: 'Q',  18: 'R',
               19: 'S',  20: 'T',  21: 'U',  22: 'V',
               23: 'W',  24: 'X',  25: 'Y',  26: 'Z'}

    # recursive call to self until we exhaust all quotients
    if colnum < (base + 1):
        return cellmap[colnum]
    else:
        return getcolumn(colnum // base) + cellmap[colnum % base]


def authenticate():
    """
    Login into Google API with oauth2
    return an instance of the interface
    """
    try:
        credentials = SignedJwtAssertionCredentials(gdoc_key['client_email'],
                                                    gdoc_key['private_key'].encode(),
                                                    GDOC_ACCESS_SCOPE)
        gc = gspread.authorize(credentials)
    except:
        raise ImproperlyConfigured("Unable to authenticate with Google Docs. "
                                   "Check oauth2 configuration under config.py")

    return gc


def open_workbook(spreadsheet_key=DEFAULT_SHEET_KEY, gc_interface=None):
    try:
        return gc_interface.open_by_key(spreadsheet_key)
    except:
        raise ImproperlyConfigured("Unable to open spreadsheet with Google Docs. "
                                   "Check sheet key, sheet permissions for client_email"
                                   "and oauth2 configuration to debug")


def delete_worksheets(workbook, first_sheet="Reference"):
    for each_worksheet in workbook.worksheets():
        if each_worksheet.title == first_sheet:
            pass
        else:
            workbook.del_worksheet(each_worksheet)


def update_cell(worksheet, cell_id="A1", value=""):
    worksheet.update_acell(label=cell_id, val=value)


def update_row(worksheet, start_row=1, start_col=1, values_list=()):
    if not values_list:
        return

    range_start = getcolumn(start_col) + str(start_row)
    range_end = getcolumn(start_col + len(values_list) - 1) + str(start_row)
    cell_list = worksheet.range(range_start + ":" + range_end)

    for i, value in enumerate(values_list):
        cell_list[i].value = value

    worksheet.update_cells(cell_list)


def update_header_row(worksheet, start_row=1, start_col=1, values_list=DEFAULT_SYNC_ROWS):
    update_row(worksheet, start_row, start_col, values_list)
