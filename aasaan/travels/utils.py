from .models import TravelRequest
from config.models import Configuration
from django.utils import formats
from datetime import date, timedelta
import json
from config.management.commands.notify_utils import dispatch_notification, setup_sendgrid_connection
from django.conf import settings

def add_travel_request_details(travel_request, ticket_details):
    ticket_row = str(ticket_details)
    ticket_row = ticket_row.replace('TRACKING NO', 'TR' + str(travel_request.id).zfill(6))
    ticket_row = ticket_row.replace('FROM', travel_request.source)
    ticket_row = ticket_row.replace('TO', travel_request.destination)

    onward_date = formats.date_format(travel_request.onward_date, "DATE_FORMAT")
    ticket_row = ticket_row.replace('DATEOFJOURNEY', onward_date)
    ticket_row = ticket_row.replace('TRAVELMODE', travel_request.get_travel_mode_display())
    ticket_row = ticket_row.replace('REMARKS', travel_request.remarks)
    traveller_details = list(travel_request.teacher.all())
    traveller_details_start = Configuration.objects.get(
        configuration_key='IPCTRAVELS_EMAIL_TRAVELLER_START_TEMPLATE').configuration_value
    traveller_row = Configuration.objects.get(
        configuration_key='IPCTRAVELS_EMAIL_TRAVELLER_LIST_TEMPLATE').configuration_value
    traveller_row = str(traveller_row)
    t_data = ''

    for index, tr in enumerate(traveller_details):
        t_row = traveller_row
        t_row = t_row.replace('#SNO#', str(index + 1))
        t_row = t_row.replace('NAME', tr.full_name)
        age = 'Age not known'
        if tr.date_of_birth:
            age = (date.today() - tr.date_of_birth) // timedelta(days=365.2425)
        t_row = t_row.replace('GENDER_AGE', tr.get_gender_display() + ' - ' + str(age))
        t_row = t_row.replace('MOBILENO', tr.primary_mobile)
        # t_row = t_row.replace('IDCARD_TYPE', tr.teacher.id_proof_type)
        # t_row = t_row.replace('IDCARDNO', tr.teacher.id_proof_number)
        t_data += t_row

    print(t_data)

    traveller_details_end = Configuration.objects.get(
        configuration_key='IPCTRAVELS_EMAIL_TRAVELLER_END_TEMPLATE').configuration_value

    return ticket_row + traveller_details_start + t_data + traveller_details_end


def sendEmailTicket(id, request):
    cft = Configuration.objects.get(configuration_key='IPCTRAVELS_EMAIL_NOTIFY')
    data = json.loads(cft.configuration_value)
    namaskaram = Configuration.objects.get(
        configuration_key='IPCTRAVELS_EMAIL_CONTENT_START_TEMPLATE').configuration_value
    ticket_details = Configuration.objects.get(
        configuration_key='IPCTRAVELS_EMAIL_TICKET_TEMPLATE').configuration_value
    pranam = Configuration.objects.get(
        configuration_key='IPCTRAVELS_EMAIL_CONTENT_END_TEMPLATE').configuration_value
    message_body = ''
    travel_request = TravelRequest.objects.get(pk=id)
    ticket_request = add_travel_request_details(travel_request, ticket_details)
    zone = travel_request.zone.zone_name
    ticket_request = ticket_request.replace('TRAVELS_INCHARGE', request.user.get_full_name())
    ticket_request = ticket_request.replace('ZONE_NAME', zone)
    travel_incharge = data[zone]['travel_incharge'].split(',')
    message_body += ticket_request

    pranam = pranam.replace('SENDER_SIGNATURE', request.user.get_full_name())
    message_body = namaskaram + message_body + pranam

    msg_subject = 'Ticket Request - TR' + str(travel_request.id).zfill(6)

    sender = request.user.email
    to = travel_incharge
    cc = [request.user.email,]
    bcc = []
    print(sender)
    print(to)
    print(request.user.email)

    sendgrid_contnection = setup_sendgrid_connection(settings.SENDGRID_KEY)
    _dispatch_status = dispatch_notification(sender, to, msg_subject,
                                             message_body, sendgrid_contnection, cc, bcc)
    if _dispatch_status:
        pass