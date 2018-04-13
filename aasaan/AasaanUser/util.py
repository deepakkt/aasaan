from threading import current_thread

_requests = {}
from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin

def get_request():
    t = current_thread()
    if t not in _requests:
        return None
    return _requests[t]


class RequestMiddleware(MiddlewareMixin):
    def process_exception(self, request, exception):
        return HttpResponse("in exception")

    def process_request(self, request):
        _requests[current_thread()] = request