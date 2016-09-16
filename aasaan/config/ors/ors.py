from requests import Request, Session
from collections import OrderedDict
import copy

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

    def create_new_program(self, program_schedule, configuration):

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

        get_config_key = lambda program, config: slugify("ors-" + program + " " + config).upper().replace("-", "_")

        create_url = "https://ors.isha.in/Program/Save"
        create_data = dict()

        try:
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
                                                     "7 days", create_data["Venue"],
                        "%s to %s" % (getformatteddate(program_schedule.start_date),
                                      getformatteddate(program_schedule.end_date))])
            create_data["AdminUserID"] = ""
            create_data["LadiesSeats"] = ""
            create_data["GentsSeats"] = ""
            create_data["TotalSeats"] = "200"
            create_data["ReservedTotalSeats"] = ""
            create_data["ProgramActiveFrom"] = ""
            create_data["ProgramActiveTo"] = ""
            create_data["ProgramDonationAmount"] = "%d" % program_schedule.donation_amount
            create_data["Volunteers"] = ""
            create_data["ZoneQuotaRestriction"] = "N"
            create_data["ValidateReceiptNo"] = "Y"
            create_data["CompanyID"] = configuration[get_config_key(program_schedule.program.name, "Hosting Company")]
            create_data["ProgramPurpose"] = configuration[get_config_key(program_schedule.program.name, "Purpose")]
            create_data["ReferenceProgramID"] = ""
            create_data["CaptureArrivalDepartureTimings"] = "N"
            create_data["BatchType"] = configuration[get_config_key(program_schedule.program.name, "Batch")]
            create_data["SpecialProgram"] = "N"
            create_data["LockProgram"] = "N"
            create_data["DarshanProgram"] = "N"
            create_data["InstantGeneration"] = "Y"
            create_data["ProgramEntity"] = configuration[get_config_key(program_schedule.program.name, "Program Entity")]
            create_data["City"] = ""
            create_data["Teacher"] = ""
            create_data["CoTeacher"] = ""
            create_data["ProgramApplicable"] = "A"
            create_data["SelectCenterCode"] = ""
            create_data["SelectCount"] = "1"
            create_data["Center"] = configuration["ORS_PROGRAM_CENTER_CODE"]
            create_data["EmergencyContact"] = "N"
            create_data["SMSProfileID"] = configuration["ORS_PROGRAM_CREATE_SMS_PROFILE_ID"]
            create_data["SMSSenderID"] = configuration["ORS_PROGRAM_CREATE_SMS_SENDER_ID"]
            create_data["ParticipantSMSMessage"] = configuration["ORS_PROGRAM_CREATE_PARTICIPANT_MSG"]
            create_data["DonorSMSMessage"] = ""
            create_data["SummarySMSMessage"] = ""
            create_data["RPSummarySMSMessage"] = ""
            create_data["BulkSMSMessage"] = ""
            create_data["CountSMSMessage"] = ""
            create_data["PCCRecipients"] = ""
            create_data["KitchenRecipients"] = ""
            create_data["FinanceRecipients"] = ""
            create_data["DefaultReportColumnName"] = ""
            create_data["IDCardValidation"] = "N"
            create_data["SenderEMailID"] = ""
            create_data["MailingInfo1"] = ""
            create_data["MailingInfo2"] = ""
            create_data["MailingInfo3"] = ""
            create_data["MailingInfo4"] = ""
            create_data["MailingInfo5"] = ""
            create_data["ThankyouScript"] = ""

            self.postrequest(request_url=create_url, request_data=create_data,
                             request_label="Create - %s" %(create_data["DisplayName"]))

            if self.last_response.status_code != 200:
                return "FAILED"

        except KeyError:
            return "FAILED"

        program_code_re = re.compile("E[0-9]{8}")

        return program_code_re.findall(self.last_response.text)[0]



