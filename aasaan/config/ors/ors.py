from requests import Request, Session
from collections import OrderedDict
import copy
from functools import partial

import re

from django.utils.text import slugify

class ORSInterface(object):
    """This class defines an interface to work with ORS, which is
    currently located at https://ors.isha.in at the time of writing
    (6-Jun-2015)

    Call authenticate to login to ORS
    self.request_history is an ordered dictionary that returns the list
    of requests and responses for the request's life time
    """

    def __init__(self, uid='', pwd='',
                 lurl="https://ors.isha.in/Security/SignIn"):
        self.userid = uid
        self.password = pwd
        self.login_url = lurl
        self.base_url = "https://ors.isha.in"
        self.headers = {"User-Agent" :"User-Agent=Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:44.0) Gecko/20100101 Firefox/44.0",
"Content-Type": "application/x-www-form-urlencoded",
"Connection": "keep-alive",
"Host" : "ors.isha.in",
"X-Requested-With": "XMLHttpRequest",
"Upgrade-Insecure-Requests": "1",
"Origin": "https://ors.isha.in",
"Accept" : "text/plain, */*; q=0.01"}
        self.login_data = OrderedDict({'Login' : self.userid,
        'Password' : self.password})

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
        """Login into ORS
        User ID and password should have been passed
        during instantiation
        """
        self.session = Session()


        headers_copy = copy.deepcopy(self.headers)

        request_init = Request('GET', self.base_url,
                               headers=headers_copy)
        prep_request = self.session.prepare_request(request_init)
        prep_response = self.session.send(prep_request, verify=self.verify,
                                        proxies=self.proxies)

        headers_copy["Cache-Control"] = "max-age=0"
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

    def create_new_program(self, program_schedule, configuration, dryrun=False):
        """Create a new program under ORS
        Warning: This program will happily create a new program even if
        the same program exists under ORS. ORS doesn't allow deleting a
        program. So call this only if you're sure the program doesn't
        exist already. The program list can be pulled from the 'getprogramlist'
        method which can be queried beforehand.

        Pass start date as a datetime object
        """

        def getformatdateddmmyy(mydate):
            return "%02d/%02d/%d" % (mydate.day, mydate.month, mydate.year)

        def getformatteddate(mydate):
            months = ['January', 'February', 'March', 'April', 'May',
            'June', 'July', 'August', 'September', 'October', 'November',
            'December']

            current_month = months[mydate.month - 1][:3]

            return "%02d-%s-%d" % (mydate.day, current_month, mydate.year)

        def get_config_key(program, config, zone=None):
            base = "ors-" + program
            if zone:
                base = base + " " + zone
            base = base + " " + config
            return slugify(base).upper().replace("-", "_")

        def parse_config(configuration_dict, program_name, program_zone_name, config,
                         fallback_value="", raise_exception=True):
            config_value = configuration_dict.get(get_config_key(program_name,
                                                                 config,
                                                                 program_zone_name))

            if not config_value:
                config_value = configuration_dict.get(get_config_key(program_name,
                                                                     config))

            if not config_value:
                if raise_exception:
                    raise KeyError
                else:
                    config_value = fallback_value

            return config_value

        create_url = "https://ors.isha.in/Program/Save"
        create_data = dict()

        try:
            _program_name = program_schedule.program.name
            _program_zone_name = program_schedule.center.zone.zone_name

            _parse_config_only = partial(parse_config, configuration, _program_name, _program_zone_name)
            _parse_config_fallback = partial(parse_config, configuration, _program_name,
                                             _program_zone_name, raise_exception=False)

            create_data["HostingCenterCode"] = ""
            create_data["IshangaRef"] = ""
            create_data["ProgramID"] = ""
            create_data["TimeStamp"] = ""
            create_data["ProgramCode"] = configuration[get_config_key(program_schedule.program.name, "Program Name")]
            create_data["Status"] = "NEW"

            languages = {'English': 'E', 'Tamil': 'T', 'Hindi': 'H'}

            # Language, ORS supports only English, Tamil and Hindi. For others, mark English
            create_data["LanguageCode"] = languages.get(program_schedule.primary_language) or "E"

            create_data["Gender"] = program_schedule.gender[0]
            create_data["ProgramStartDate"] = getformatdateddmmyy(program_schedule.start_date)
            create_data["ProgramEndDate"] = getformatdateddmmyy(program_schedule.end_date)
            create_data["Venue"] = program_schedule.program_location
            create_data["DisplayName"] = " - ".join([program_schedule.program.name,
                                                     program_schedule.center.center_name,
                                                     getformatteddate(program_schedule.start_date)])
            create_data["AdminUserID"] = ""
            create_data["LadiesSeats"] = ""
            create_data["GentsSeats"] = ""
            create_data["TotalSeats"] = _parse_config_fallback("Total Seats", "200")
            create_data["ReservedTotalSeats"] = _parse_config_fallback("Reserved Total Seats")
            create_data["ProgramActiveFrom"] = _parse_config_fallback("Program Active From")
            create_data["ProgramActiveTo"] = _parse_config_fallback("Program Active To")
            create_data["ProgramDonationAmount"] = "%d" % program_schedule.donation_amount
            create_data["Volunteers"] = _parse_config_fallback("Volunteers")
            create_data["ZoneQuotaRestriction"] = _parse_config_fallback("Zone Quota Restriction", "N")
            create_data["ValidateReceiptNo"] = _parse_config_fallback("Validate Receipt No", "Y")
            create_data["CompanyID"] = _parse_config_only("Hosting Company")
            create_data["ProgramPurpose"] = _parse_config_only("Purpose")
            create_data["ReferenceProgramID"] = _parse_config_fallback("Reference Program ID")
            create_data["CaptureArrivalDepartureTimings"] = _parse_config_fallback("Capture Arrival Departure Timings",
                                                                                   "N")
            create_data["BatchType"] = _parse_config_only("Batch")
            create_data["SpecialProgram"] = _parse_config_fallback("Special Program", "N")
            create_data["LockProgram"] = _parse_config_fallback("Lock Program", "N")
            create_data["DarshanProgram"] = _parse_config_fallback("Darshan Program", "N")
            create_data["InstantGeneration"] = _parse_config_fallback("Instant Generation", "Y")
            create_data["ProgramEntity"] = _parse_config_only("Program Entity")
            create_data["City"] = _parse_config_fallback("City")
            create_data["Teacher"] = _parse_config_fallback("Teacher")
            create_data["CoTeacher"] = _parse_config_fallback("Co Teacher")
            create_data["ProgramApplicable"] = _parse_config_fallback("Program Applicable", "A")
            create_data["SelectCenterCode"] = _parse_config_fallback("Select Center Code")
            create_data["SelectCount"] = _parse_config_fallback("Select Count", "1")
            create_data["Center"] = configuration["ORS_PROGRAM_CENTER_CODE"]
            create_data["EmergencyContact"] = _parse_config_fallback("Emergency Contact", "N")
            create_data["SMSProfileID"] = configuration["ORS_PROGRAM_CREATE_SMS_PROFILE_ID"]
            create_data["SMSSenderID"] = configuration["ORS_PROGRAM_CREATE_SMS_SENDER_ID"]
            create_data["ParticipantSMSMessage"] = configuration["ORS_PROGRAM_CREATE_PARTICIPANT_MSG"]
            create_data["DonorSMSMessage"] = _parse_config_fallback("Donor SMS Message")
            create_data["SummarySMSMessage"] = _parse_config_fallback("Summary SMS Message")
            create_data["RPSummarySMSMessage"] = _parse_config_fallback("RP Summary SMS Message")
            create_data["BulkSMSMessage"] = _parse_config_fallback("Bulk SMS Message")
            create_data["CountSMSMessage"] = _parse_config_fallback("Count SMS Message")
            create_data["PCCRecipients"] = _parse_config_fallback("PCC Recipients")
            create_data["KitchenRecipients"] = _parse_config_fallback("Kitchen Recipients")
            create_data["FinanceRecipients"] = _parse_config_fallback("Finance Recipients")
            create_data["DefaultReportColumnName"] = _parse_config_fallback("Default Report Column Name")
            create_data["IDCardValidation"] = _parse_config_fallback("ID Card Validation", "N")
            create_data["SenderEMailID"] = _parse_config_fallback("Sender EMail ID")
            create_data["MailingInfo1"] = _parse_config_fallback("Mailing Info 1")
            create_data["MailingInfo2"] = _parse_config_fallback("Mailing Info 2")
            create_data["MailingInfo3"] = _parse_config_fallback("Mailing Info 3")
            create_data["MailingInfo4"] = _parse_config_fallback("Mailing Info 4")
            create_data["MailingInfo5"] = _parse_config_fallback("Mailing Info 5")
            create_data["ThankyouScript"] = _parse_config_fallback("Thank You Script")

            if not dryrun:
                self.postrequest(request_url=create_url, request_data=create_data,
                                 request_label="Create - %s" %(create_data["DisplayName"]))

                if self.last_response.status_code != 200:
                    return "FAILED"

        except KeyError:
            return "FAILED"

        if not dryrun:
            program_code_re = re.compile("E[0-9]{8}")

            return program_code_re.findall(self.last_response.text)[0]
        else:
            return "E99999999"
