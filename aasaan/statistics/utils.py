import datetime
from dateutil.rrule import rrule, MONTHLY

def get_date_list_now():
    strt_dt = datetime.datetime.today()
    end_dt = datetime.date.today() - datetime.timedelta(6 * 365 / 12)
    date_list = [dt.strftime("%Y-%m") for dt in rrule(MONTHLY, dtstart=end_dt,
                                                  until=strt_dt)]
    date_list.sort()
    return date_list[:6]

def get_date_list(start_date, end_date):
    sdate = datetime.datetime.strptime(start_date, "%Y-%m").date()
    edate = datetime.datetime.strptime(end_date, "%Y-%m").date()
    date_list = [dt.strftime("%Y-%m") for dt in rrule(MONTHLY, dtstart=sdate,
                                                      until=edate)]
    date_list.sort()
    return date_list

