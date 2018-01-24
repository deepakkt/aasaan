from requests import Request, Session
from collections import OrderedDict
import pandas as pd
import json
import datetime
from utils.datedeux import DateDeux
import copy


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

class EReceiptsInterface(object):
    """This class defines an interface to work with ORS, which is 
    currently located at https://ors.isha.in at the time of writing
    (6-Jun-2015)
    
    Call authenticate to login to ORS
    self.request_history is an ordered dictionary that returns the list
    of requests and responses for the request's life time
    """
    
    def __init__(self, uid='', 
                 pwd='', 
                 lurl="https://www.ereceipts.in/login.php"):
        self.userid = uid
        self.password = pwd
        self.login_url = lurl
        self.base_url = "https://www.ereceipts.in"
        
        self.headers = {"User-Agent" :"User-Agent=Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:44.0) Gecko/20100101 Firefox/44.0",
"Content-Type": "application/x-www-form-urlencoded", 
"Connection": "keep-alive",
"Accept-Encoding": "gzip, deflate, br",
"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
"Host" : "www.ereceipts.in",
"Origin": "https://www.ereceipts.in",
"Referer": "https://www.ereceipts.in/login.php?s=1",
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
        """Login into ereceipts
        User ID and password should have been passed
        during instantiation
        """      
        self.session = Session()
        

        headers_copy = copy.deepcopy(self.headers)

        request_init = Request('GET', self.base_url,
                               headers=headers_copy)
        self.prep_request = self.session.prepare_request(request_init)
        self.prep_response = self.session.send(self.prep_request, verify=self.verify,
                                        proxies=self.proxies)                                     

        headers_copy["Cache-Control"] = "max-age=0"

        
        self.login_data = {'username': self.userid,
                           'password': self.password,
                           'do': "login"}

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
                
        if querystring:
            _request_url = Request('GET', request_url,
                               params=querystring).prepare().url
        else:
            _request_url = request_url
        
        current_request = Request(method, _request_url, data=request_data, 
                                  headers=self.headers)  
                                  
        self.last_request = self.session.prepare_request(current_request)
        
        self.last_response = self.session.send(self.last_request, stream=True, 
                                               verify=self.verify,
                                               proxies=self.proxies)
        self.last_request_label = request_label
        
        self._append_request()
        
        #restore header from copy
        self.headers = headers_copy
        
        
    def get_receipts(self, start_date=None, end_date=None, 
                    collection="ereceipts_IshaInstituteofInnerSciences_1718",
                    report="IYP Donation List IIIS"):
        if not start_date:
            _start_date = DateDeux.today().monthstart()
            #_end_date = DateDeux.today().monthend()
            _end_date = _start_date
        else:
            _start_date = DateDeux.frompydate(start_date)
            _end_date = DateDeux.frompydate(end_date)
            
        _start_date = _start_date.dateformat("dd-mm-yyyy")
        _end_date = _end_date.dateformat("dd-mm-yyyy")
            
        #_collection = "ereceipts_IshaInstituteofInnerSciences_1718"            
        #_collection = "ereceipts_IshaFoundation_1718"
        _collection = collection
        _context = '{"collection": "%s"}' % (_collection)
        #_report = "IYP Donation List IIIS"
        #_report = "IYP Donation List"
        _report = report
        _fields = '{"zone":1,"center":1,"entity":1,"purpose":1,"eReceiptDate":1,"eBookNumber":1,"eReceiptNumber":1,"amount":1,"mode":1,"instnum":1,"instdate":1,"chequeClearingStatus":1,"chequeBounceReason":1,"ccTerminalId":1,"ccApprovalCode":1,"bankname":1,"branchname":1,"rpsNumber":1,"challanNumber":1,"challanDepositedBank":1,"brsStatus":1,"depositedDate":1,"name":1,"address":1,"city":1,"state":1,"pincode":1,"country":1,"mobile":1,"email":1,"nationality":1,"phone":1,"transref":1,"programcode":1,"pan":1,"towards":1,"raiser":1,"comments":1,"brsDate":1,"signed":1,"emailDate":1,"smsDate":1,"passcode":1,"tallyProgramcode":1}'
        _hook = ''
        _hookArgs = ''
        _sidx = '_id'
        _condition = '{"dateOfReceipt":"range,%s,%s"}' % (_start_date, _end_date)
        _page = "1"
        _rows = "5000"
        _nd = str(datetime.datetime.now().timestamp()).split(".")[0]
        _totalrows = "100"
        _sord = "asc"
        _search = "false"
        _splice = "none"
        
        request_data = {
            "hook" : _hook,
            "hookArgs" : _hookArgs,
            "sidx" : _sidx,
            "context" : _context,
            "condition": _condition,
            "fields" : _fields,
            "page": _page,
            "rows" : _rows,
            "nd": _nd,
            "totalrows": _totalrows,
            "sord" : _sord,
            "_search" : _search,
            "splice": _splice
        }
        
        querystring_data = {
            "collname" : _collection,
            "reportname" : _report
        }
        
        receipt_url = "https://www.ereceipts.in/db2.php"
        
        self.postrequest(request_data=request_data, 
                         querystring=querystring_data,
                         request_url=receipt_url,
                         request_label="Get Receipts Data")

        receipts = json.loads(self.last_response.text)
        return receipts["rows"]


    def pretty_print_request(self):
        """
        At this point it is completely built and ready
        to be fired; it is "prepared".
    
        However pay attention at the formatting used in 
        this function because it is programmed to be pretty 
        printed and may differ from the actual request.
        """
        req = self.last_request
        print('{}\n{}\n{}\n\n{}'.format(
            '-----------START-----------',
            req.method + ' ' + req.url,
            '\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
            req.body,
        ))

        
        
if __name__ == "__main__":
    
    #Simple tests to see if the class works as intended
    myj = EReceiptsInterface()
    myj.authenticate()
    receipts = myj.get_receipts()
    print(receipts)
