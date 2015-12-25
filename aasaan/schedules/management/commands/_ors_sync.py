from requests import Request, Session
import json
import datetime
import os

#change below for deployment to prod
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aasaan.settings.dev-deepak')

import django
django.setup()

from django.conf import settings


def json_date_as_datetime(jd):
    """default json serializaiton of date and time
    happens once in a while. json doesn't support it
    so this function de-serializes it and returns
    a python datetime function
    """

    sign = jd[-7]
    if sign not in '-+' or len(jd) == 13:
        millisecs = int(jd[6:-2])
    else:
        millisecs = int(jd[6:-7])
        hh = int(jd[-7:-4])
        mm = int(jd[-4:-2])
        if sign == '-': mm = -mm
        millisecs += (hh * 60 + mm) * 60000
    return datetime.datetime(1970, 1, 1) \
        + datetime.timedelta(microseconds=millisecs * 1000)


def adjuststartdate(sd):
    if not sd:
        return ""

    tempdate = datetime.date(json_date_as_datetime(sd).year,
                             json_date_as_datetime(sd).month,
                             json_date_as_datetime(sd).day)
    return datetime.date.fromordinal(tempdate.toordinal() + 1)


def ors_authenticate():
    session = Session()
    login_url = r"https://ors.isha.in/Security/SignIn"
    login_data = {'Login' : settings.ORS_USER,
    'Password' : settings.ORS_PASSWORD}
    headers = {"User-Agent" :"Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.152 Safari/537.36",
"Content-Type": "application/x-www-form-urlencoded",
"Connection": "keep-alive",
"Host" : "ors.isha.in",
"X-Requested-With": "XMLHttpRequest",
"Upgrade-Insecure-Requests": "1",
"Origin": "https://ors.isha.in",
"Accept" : "text/plain, */*; q=0.01"}

    login_prep = Request('POST', login_url,
                                 data=login_data,
                                 headers=headers)
    login_request = session.prepare_request(login_prep)
    login_response = session.send(login_request)

    if login_response.status_code in [200, 302]:
        return session
    else:
        return False


def ors_get_program_list(session, program_filter='IYP', date_filter=None):
    if not session:
        return False

    headers = {"User-Agent" :"Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.152 Safari/537.36",
"Content-Type": "application/x-www-form-urlencoded",
"Connection": "keep-alive",
"Host" : "ors.isha.in",
"X-Requested-With": "XMLHttpRequest",
"Upgrade-Insecure-Requests": "1",
"Origin": "https://ors.isha.in",
"Accept" : "text/plain, */*; q=0.01"}

    programlist_url = "https://ors.isha.in/Program/RefreshProgram"

    if date_filter:
        date_iso = datetime.date.today().isoformat() + "T00-00-00"
        request_parms = "page=1&size=5000&filter=StartDate~ge~datetime" + "'" + date_iso + "'"
    else:
        request_parms = "page=1&size=5000"

    current_request = Request('POST', programlist_url, data=request_parms,
                              headers=headers)

    prep_request = session.prepare_request(current_request)
    prep_request_response = session.send(prep_request)

    program_list_json = json.loads(prep_request_response.text)

    program_list = []

    for each_program in program_list_json['data']:
        new_program = dict()
        if each_program['ProgramCode'] == 'IYP':
            new_program['ProgramID'] = each_program['ProgramID']
            new_program['ProgramName'] = each_program['ProgramName']
            new_program['ProgramCode'] = each_program['ProgramCode']
            new_program['StartDate'] = adjuststartdate(each_program['StartDate'])
            new_program['Center'] = each_program['ProgramVenue']
            program_list.append(new_program)

    return program_list


if __name__ == "__main__":
    my_session = ors_authenticate()
    if my_session:
        import pprint
        mydata = ors_get_program_list(my_session, date_filter=True)
        pprint.pprint(mydata)
    else:
        print("Authentication failed")
