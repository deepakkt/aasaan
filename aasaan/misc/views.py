import json
from functools import partial
from datetime import date
import random

from django.shortcuts import render
from django.contrib import messages
from django.views.generic import View
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from contacts.models import Zone, Center
from .models import LocalEvents

from .forms import LocalEventsForm

from gsync.sync.sync_v2 import sync_schedules_test

try:
    import django_rq
except (ImportError, ImproperlyConfigured):
    pass


# Create your views here.

class LocalEventsView(View):
    template = "misc/local_events.html"

    def get_zones_and_centers(self):
        zone_center_list = [{'zone': x.zone_name,
                             'centers': [y.center_name for y in x.center_set.all()]}
                            for x in Zone.objects.all()]

        return json.dumps(zone_center_list).replace("'", "\\u0027")

    def get_context(self, request):
        return {'messages': messages.get_messages(request),
         'zones': self.get_zones_and_centers()}

    def get(self, request, *args, **kwargs):
        return render(request, self.template, self.get_context(request))

    def populate_model(self, model, form, attribute, morpher=None):
        morpher_final = morpher or (lambda x: x)
        setattr(model, attribute, morpher_final(form.cleaned_data.get(attribute)))

    def post(self, request, *args, **kwargs):
        event = LocalEventsForm(request.POST)

        if event.is_valid():
            new_event = LocalEvents()
            __ = partial(self.populate_model, new_event, event)

            new_event.admin_approved = False
            new_event.zone = Zone.objects.get(zone_name=event.cleaned_data['zone'])
            new_event.center = Center.objects.get(zone=new_event.zone,
                                                  center_name=event.cleaned_data['center'])
            __('submitter_name')
            __('submitter_mobile')
            __('event_category')
            __('event_name')
            __('number_of_people', int)
            __('people_category')
            __('event_details')
            __('isha_aspect')
            __('event_name')
            __('event_start_date')
            __('event_end_date')
            __('event_timing')
            __('event_venue')
            __('event_city')
            __('event_entry_category')
            __('event_organizer_contact')
            __('event_url')
            __('ashram_contact_name')
            __('ashram_contact_mobile')
            __('final_remarks')

            new_event.save()

            messages.success(request, "%s was submitted successfully. You may submit another event if you wish." % new_event)
            return render(request, self.template, self.get_context(request))
        else:
            print(event.errors)


@method_decorator(csrf_exempt, name='dispatch')
class AdminDashboardDispatch(View):
    template = "misc/synch_sheets.html"

    def get(self, request, *args, **kwargs):
        return render(request, self.template)

    def trigger_async(self, func):
        if settings.ASYNC:
            job = django_rq.enqueue(func)
            return {'message': 'Sync queued successfully with id ' % job.id,
                    'code': 'success'}
        else:
            return {'message': 'RQ is not setup. Cannot queue sync',
                    'code': 'error'}


    def post(self, request, *args, **kwargs):
        incoming_parms = request.POST

        submitted_command = incoming_parms['command']

        if submitted_command == "sync_schedules":
            cmd_queue = self.trigger_async(sync_schedules_test)
            return JsonResponse(cmd_queue)

        return HttpResponse()

