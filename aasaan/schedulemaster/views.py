from datetime import datetime

from django.shortcuts import render
from django.http import Http404
from .models import ProgramSchedule

from utils.datedeux import DateDeux

# Create your views here.

def display_single_schedule(request, schedule_id):
    try:
        schedule = ProgramSchedule.objects.get(id=int(schedule_id))
    except:
        raise Http404("Schedule does not exist")

    schedule_data = {
        'program': schedule.program.name,
        'center': schedule.center.center_name,
        'zone': schedule.center.zone.zone_name,
        'start_date': DateDeux.frompydate(schedule.start_date).dateformat("dd-mmm-yyyy"),
        'end_date': DateDeux.frompydate(schedule.end_date).dateformat("dd-mmm-yyyy"),
        'fee': schedule.donation_amount,
        'offline_reg_code': schedule.event_management_code,
        'online_reg_code': schedule.online_registration_code,
        'contact': '%s @ %s, %s' % (schedule.contact_name or "Unknown",
                                    schedule.contact_email,
                                    schedule.contact_phone1),
        'timestamp': datetime.now()
        }

    return render(request, "schedulemaster/view_single_program.html", {'schedule': 
                                                                        schedule_data})
