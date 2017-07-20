'''Copyright 2017, Deepak

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''

from datetime import date, datetime
from functools import partial
import re

class DateDeux(date):
    def pydate(self):
        return date(self.year, self.month, self.day)

    @classmethod
    def fromisodate(self, isodatestr):
        try:
            return DateDeux(*(map(int, isodatestr.split('-'))))
        except:
            return None

    @classmethod
    def frompydate(self, pydate_object):
        return DateDeux(pydate_object.year, pydate_object.month, pydate_object.day)            

    def monthstart(self):
        return DateDeux(self.year, self.month, 1)

    def monthend(self):
        return DateDeux.fromordinal(DateDeux(self.year, self.month + 1, 1).toordinal() - 1)

    def yearend(self):
        return DateDeux(self.year, 12, 31)

    def yearstart(self):
        return DateDeux(self.year, 1, 1)

    def dayname(self):
        return ['Monday', 'Tuesday', 'Wednesday',
                'Thursday', 'Friday', 'Saturday', 'Sunday'][self.weekday()]

    def dayname_short(self):
        return self.dayname()[:3]

    def monthname(self):
        return ['', 'January', 'February', 'March', 'April', 'May', 'June',
                'July', 'August', 'September', 'October', 
                'November', 'December'][self.month]

    def monthname_short(self):
        return self.monthname()[:3]

    def dateformat(self, format):
        def _format_as_int(number, length):
            if length < len(str(number)):
                return str(number)[-length:]

            format = "%%0%dd" % length
            return format % number

        def _format_month(*args):
            return self.monthname_short()

        def _re_match(matchstring, regex):
            return re.findall(regex, matchstring)[0]

        matches = list(map(partial(_re_match, format), ['y+', 'm+', 'd+']))

        result = format[:]
        result = result.replace(matches[0], _format_as_int(self.year, len(matches[0])))
        result = result.replace(matches[2], _format_as_int(self.day, len(matches[2])))
        _month_func = _format_month if len(matches[1]) == 3 else _format_as_int
        result = result.replace(matches[1], _month_func(self.month, len(matches[1])))
        return result

    def yearcalendar(self):
        _start = DateDeux(self.year, 1, 1)
        _end = DateDeux(self.year, 12, 31)

        diff = _end.toordinal() - _start.toordinal() + 1
        return (_start + x for x in range(0, diff))

    def monthcalendar(self):
        _start = self.monthstart()
        _end = self.monthend()

        diff = _end.toordinal() - _start.toordinal() + 1
        return (_start + x for x in range(0, diff))

    def __add__(self, numdays):
        return DateDeux.fromordinal(self.toordinal() + numdays)

    def __sub__(self, numdays):
        try:
            return self.toordinal() - numdays.toordinal()
        except AttributeError:
            return DateDeux.fromordinal(self.toordinal() - numdays)

    def __iter__(self):
        return iter((self.year, self.month, self.day))
