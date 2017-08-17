from functools import partial
from requests import Request, Session
from collections import OrderedDict
import json
import datetime
import copy
from bs4 import BeautifulSoup
from requests_toolbelt.multipart.encoder import MultipartEncoder

from django.utils.text import slugify

from config.config_utils import *

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

class JoomlaInterface(object):
    """This class defines an interface to work with ORS, which is
    currently located at https://ors.isha.in at the time of writing
    (6-Jun-2015)

    Call authenticate to login to ORS
    self.request_history is an ordered dictionary that returns the list
    of requests and responses for the request's life time
    """

    def __init__(self, uid='#',
                 pwd='#',
                 lurl="https://www.ishafoundation.org/administrator/"):
        self.session = Session()
        self.userid = uid
        self.password = pwd
        self.login_url = lurl + "index.php"
        self.base_url = lurl
        self.headers = {"User-Agent" :"User-Agent=Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:44.0) Gecko/20100101 Firefox/44.0",
"Content-Type": "application/x-www-form-urlencoded",
"Connection": "keep-alive",
"Host" : "www.ishafoundation.org",
"Origin": "https://www.ishafoundation.org",
"Referer": "https://www.ishafoundation.org/administrator/",
"Upgrade-Insecure-Requests": "1"}

        #Remember the history of requests
        self.request_history = OrderedDict()
        self.verify = True
        self.proxies = None

    def _append_request(self, login=False):
        """Internal book keeping module
        Do not touch or modify
        """
        numrequests = len(self.request_history) + 1
        if login:
            self.request_history["%d - Login" %(numrequests)] = (self.login_request, self.login_response)
        else:
            self.request_history["%d - %s" %(numrequests, self.last_request_label)] = (self.last_request, self.last_response)


    def authenticate(self):
        """Login into Joomla
        User ID and password should have been passed
        during instantiation
        """
        headers_copy = copy.deepcopy(self.headers)

        request_init = Request('GET', self.base_url,
                               headers=headers_copy)
        self.last_request = self.session.prepare_request(request_init)
        self.last_response = self.session.send(self.last_request, verify=self.verify,
                                        proxies=self.proxies)
        self.last_request_label = "Pre-login fetch"

        self._append_request()

        if self.last_response.status_code != 200:
            return False

        soup = BeautifulSoup(self.last_response.text, "html.parser")
        csrf_token = soup.find_all('input')[-1]['name']
        headers_copy['Content-Type'] = "application/x-www-form-urlencoded"

        self.login_data = {'username': self.userid,
                           'passwd': self.password,
                           'lang': "",
                           'option': "com_login",
                           'task': "login",
                           csrf_token: "1"}

        login_prep = Request('POST', self.login_url,
                                     data=self.login_data,
                                     #cookies=session_cookie,
                                     headers=headers_copy)
        self.login_request = self.session.prepare_request(login_prep)
        self.login_response = self.session.send(self.login_request,
                                                verify=self.verify,
                                                proxies=self.proxies)

        self._append_request(login=True)

        if self.login_response.status_code in [200, 302]:
            return True
        else:
            return False

    def postrequest(self, method='POST', querystring=None,
                    request_data=None, request_url="",
                    request_label = "", headers=None, del_headers=None):

        """There should be no need to call this method directly
        However, if the built in methods do not suffice,
        this method can be called to fulfill a requirement.
        Authenticate first
        """
        #append header parameters to the object's request pipeline

        #copy current headers as the caller might want to change them
        headers_copy = copy.deepcopy(self.headers)

        if headers:
            for eachkey in headers:
                self.headers[eachkey] = headers[eachkey]

        if del_headers:
            for eachkey in del_headers:
                del self.headers[eachkey]

        current_request = Request(method, request_url, data=request_data,
                                  headers=self.headers)

        self.last_request = self.session.prepare_request(current_request)

        self.last_response = self.session.send(self.last_request, stream=True,
                                               verify=self.verify,
                                               proxies=self.proxies)
        self.last_request_label = request_label

        self._append_request()

        #restore header from copy
        self.headers = headers_copy

    def filter_program(self, program_description=""):
        filter_url = "https://www.ishafoundation.org/administrator/"
        "index.php?option=com_program&task=listprograms"

        filter_parms = {"search" : program_description[:50],
                        "limit": "50",
                        "limitstart": "0",
                        "option": "com_program",
                        "boxchecked": "0",
                        "controller": "program",
                        "task": "listprograms",
                        "filter_order": "session_id",
                        "filter_order_Dir": ""}

        self.headers['Content-Type'] = "application/x-www-form-urlencoded"

        self.postrequest(request_url=filter_url,
                         request_data=filter_parms,
                         request_label="Search for program")


        if self.last_response.status_code != 200:
            return False

        soup = BeautifulSoup(self.last_response.text, "html.parser")

        try:
            jc = [x for x in soup.find_all('input') if x.get('id')][0]['value']
            return jc
        except:
            return "FAILED?"


    def update_program(self, fieldset=dict(), boundary=""):
        multipart_data = MultipartEncoder(
        fields= fieldset,
        boundary=boundary)

        self.headers['Content-Type'] = multipart_data.content_type


        self.postrequest(request_url="https://www.ishafoundation.org/administrator/index.php",
        request_data = multipart_data,
        headers=self.headers
        )

    def create_new_program(self, program_schedule, config):

        _program_name = program_schedule.program.name
        _program_zone_name = program_schedule.center.zone.zone_name

        _parse_config_fallback = partial(parse_config, config, _program_name,
                                         _program_zone_name, raise_exception=False,
                                         prefix='JOOMLA-')

        feedata_create = """[{"id":"5131","amount":"***donationamount***","quota":"0","name":""},{"amount":"<input type="text" id="fAmount" name="fAmount" value="">","quota":"<input type="text" id="fQuota" name="fQuota" value="">","name":"<input type="text" id="fName" name="fName" value="">"}]"""
        feedata_update = """[{"amount":"***donationamount***","quota":"","name":""},{"amount":"<input type="text" id="fAmount" name="fAmount" value="">","quota":"<input type="text" id="fQuota" name="fQuota" value="">","name":"<input type="text" id="fName" name="fName" value="">"}]"""

        base_fields= {
        'isha_title': '**tofill**',
        'title': '**tofill**',
        'session_up_date': '**tofill**',
        'session_up_hrs': '00',
        'session_up_mins': '00',
        'session_down_date': '**tofill**',
        'session_down_hrs': '00',
        'session_down_mins': '00',
        'published': '1',
        'is_hidden': '',
        'cat_id': '**tofill**',
        'is_meditator_only': '',
        'no_seats': '',
        'is_prereg_enabled': '**tofill**',
        'is_reg_enabled': '1',
        'prereg_link': "",
        'is_online_reg_enabled': '**tofill**',
        'prog_closed_text': "",
        #'is_hide_prebutton': '1',
        'language': '**tofill**',
        'gender': 'unspecified',
        'show_language': '1',
        'no_free_talk_first_day': '',
        'intro_time': '',
        'first_session_time': '',
        'x_intro1_details': "",
        'x_intro2_details': "",
        'x_intro3_details': "",
        'custom_text': "",
        'usd_donation': '0',
        'indian_donation': '0',
        'uk_donation': '0',
        'll_donation': '0',
        'c_name_1': '',
        'c_phone_1': '**tofill**',
        'c_email_1': '**tofill**',
        'c_name_2': '',
        'c_phone_2': '',
        'c_email_2': '',
        'session_time1': '',
        'session_time2': '',
        'session_time3': '',
        'override_session_timings': '',
        'reporting_time': '',
        'closing_time': '',
        'eflyer_url': '',
        'c_name_3': '',
        'c_phone_3': '',
        'c_email_3': '',
        'venue_id': '0',
        'session_specific': '1',
        'name': '**tofill**',
        'address': '**tofill**',
        'locale': '**tofill**',
        'city': '**tofill**',
        'state': '',
        'postalcode': '',
        'country': 'IN',
        'location_note': '',
        'custom_map_url': '',
        'option': 'com_program',
        'cid': '0',
        'session_id': '0',
        'task': 'save',
        'controller': 'program',
        'events_id': '0',
        'session_up': '**tofill**',
        'session_down': '**tofill**',
        'google_map_link': '**tofill**',
        'user_id': '7886',
        'fCurrency': '2',
        'fAmount': '',
        'fQuota': '',
        'fName': '',
        'feeids': "5131,5418,5489,5565,5867,8435,8436,8437,8438,32687,33112,54197,54213,54216,54242,54329,54769,54775",
        #'feedata': """[{"id":"5131","amount":"***donationamount***","quota":"0","name":""},{"amount":"<input type=\"text\" id=\"fAmount\" name=\"fAmount\" value=\"\">","quota":"<input type=\"text\" id=\"fQuota\" name=\"fQuota\" value=\"\">","name":"<input type=\"text\" id=\"fName\" name=\"fName\" value=\"\">"}]"""
        'feedata': """[{"id":"5131","amount":"1000","quota":"0","name":""},{"amount":"<input type="text" id="fAmount" name="fAmount" value="">","quota":"<input type="text" id="fQuota" name="fQuota" value="">","name":"<input type="text" id="fName" name="fName" value="">"}]"""
           }

        additional_joomla_settings = program_schedule.joomla_configurations

        base_fields['title'] = " - ".join([program_schedule.program.name,
                                           str(program_schedule.id)])
        base_fields['isha_title'] = ""
        base_fields['session_up_date'] = program_schedule.start_date.isoformat()
        base_fields['session_up'] = base_fields['session_up_date']
        base_fields['session_down_date'] = program_schedule.end_date.isoformat()
        base_fields['session_down'] = base_fields['session_down_date']
        base_fields['cat_id'] = _parse_config_fallback('cat id', '8')
        base_fields['is_prereg_enabled'] = _parse_config_fallback('is prereg enabled', "0")
        base_fields['is_online_reg_enabled'] = base_fields['is_prereg_enabled']
        base_fields['language'] = program_schedule.primary_language.name.lower()
        base_fields['c_email_1'] = program_schedule.contact_email
        base_fields['c_phone_1'] = program_schedule.contact_phone1
        base_fields['c_phone_2'] = program_schedule.contact_phone2
        base_fields['zone'] = _parse_config_fallback('zone', "None")
        base_fields['name'] = program_schedule.venue_name
        _city = program_schedule.center.city
        _center = program_schedule.center.center_name
        _eflyer_url = additional_joomla_settings.get('JOOMLA_EFLYER_URL') or ""
        base_fields['locale'] = "" if _center == _city else _center
        base_fields['intro_time'] = additional_joomla_settings.get('JOOMLA_INTRO_TIME') or ""
        base_fields['custom_text'] = additional_joomla_settings.get('JOOMLA_CUSTOM_TEXT') or ""
        base_fields['override_session_timings'] = additional_joomla_settings.get('JOOMLA_SESSION_TIME') or ""
        base_fields['eflyer_url'] = "" if _eflyer_url == "None" else _eflyer_url
        base_fields['google_map_link'] = program_schedule.google_map_url
        base_fields['address'] = program_schedule.venue_address
        base_fields['city'] = _city
        base_fields['no_free_talk_first_day'] = {'1': '1', 'Yes': ''}[_parse_config_fallback('free intro enabled', '1')]

        feedata_create = feedata_create.replace('***donationamount***', str(program_schedule.donation_amount))
        feedata_update = feedata_update.replace('***donationamount***', str(program_schedule.donation_amount))

        form_boundary = config.get('JOOMLA_FORM_BOUNDARY') or '----SomeMadeUpBoundaryAsThamuDidntPutOne'

        base_fields['feedata'] = feedata_create
        self.update_program(base_fields, form_boundary)

        if self.last_response.status_code != 200:
            return 'FAILED'

        joomla_code = self.filter_program(base_fields['title'])

        if joomla_code.startswith('FAILED'):
            return joomla_code

        base_fields['feeids'] = ""
        base_fields['feedata'] = feedata_update
        base_fields['cid'] = joomla_code
        base_fields['session_id'] = joomla_code
        base_fields['events_id'] = joomla_code
        self.update_program(base_fields, form_boundary)

        if self.last_response.status_code != 200:
            return 'FAILED-II'

        return joomla_code
        

    def get_paid_count(self, program_id):
        paid_count_url = "https://www.ishafoundation.org/administrator/index.php?option=com_program&controller=prgregister"

        filter_parms = {"process" : "filter",
                        "task": "",
                        "program_type": "",
                        "status": "confirmed",
                        "prg": str(program_id),
                        "type": "",
                        "start_date": "",
                        "end_date": "",
                        "location": "india",
                        "limit": "0",
                        "limitstart": "0"}

        self.postrequest(request_url=paid_count_url,
                         request_data=filter_parms,
                         request_label="Filter paid count")
                         
        
        if self.last_response.status_code != 200:
            return False
            
        soup = BeautifulSoup(self.last_response.text, "html.parser")
        
        return len(soup.select(".adminlist")[0].find_all("tr")) - 2



if __name__ == "__main__":

    #Simple tests to see if the class works as intended
    myj = JoomlaInterface()
    myj.authenticate()
    #result = myj.update_program('11563')