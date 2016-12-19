from django.views.generic.edit import FormView
from django.shortcuts import render
from django.http import HttpResponse
from .forms import SummaryForm
from contacts.models import Zone
from .models import TravellerDetails, BookingDetails, TravelRequest, TravelModeMaster, AgentMaster
import datetime
from django.utils.dateparse import parse_date
import dateutil.parser

class SummaryView(FormView):
    def get(self, request, *args, **kwargs):
        return render(request, 'ipctravels/travel_report.html', {'form': SummaryForm()})


class ReportView(FormView):
    def post(self, request, *args, **kwargs):
        status = request.POST.get('status')
        journey_start_date = dateutil.parser.parse(request.POST.get('journey_start_date'))
        journey_end_date = dateutil.parser.parse(request.POST.get('journey_end_date'))
        booking_start_date = dateutil.parser.parse(request.POST.get('booking_start_date'))
        booking_end_date = dateutil.parser.parse(request.POST.get('booking_end_date'))
        travel_mode = TravelModeMaster.objects.get(pk=request.POST.get('travel_mode'))
        agent = AgentMaster.objects.get(pk=request.POST.get('agent'))
        zone = request.POST.getlist('zone')
        zone_list = Zone.objects.filter(pk__in=zone)
        TravelRequest.objects.filter(status=status)
        print(journey_start_date)
        print(journey_end_date)
        bd = BookingDetails.objects.filter(date_of_journey__range=(journey_start_date, journey_end_date))
        bd = bd.filter(date_of_booking__range=(booking_start_date, booking_end_date))
        bd = bd.filter(travel_mode=travel_mode)
        bd = bd.filter(booked_by=agent)
        print('==========')
        print(bd)
        td = TravellerDetails.objects.filter(zone__in=zone_list)
        print(td)
        return render(request, 'ipctravels/travel_report.html', {'form': SummaryForm()})
