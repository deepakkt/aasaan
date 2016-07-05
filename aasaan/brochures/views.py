import json
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import BrochureSetItem, Brochures, StockPointMaster, BrochureMaster
from schedulemaster.models import ProgramSchedule
from contacts.models import Zone
from django.conf import settings


@login_required
def get_brochure_list(request):
    brochure_list = []
    if request.method == 'GET':
        stock_id = request.GET['source_stock_point']
        brochure_list = [(x.item.pk, x.quantity) for x in
                     Brochures.objects.filter(stock_point=StockPointMaster.objects.get(pk__in=stock_id))]
    return JsonResponse(brochure_list, safe=False)


@login_required
def get_brochure_set(request):
    if request.method == 'GET':
        brochure_set = request.GET['brochure_set']
    brochure_list = [(x.item.pk, x.quantity) for x in BrochureSetItem.objects.filter(brochure_set=brochure_set)]
    return JsonResponse(brochure_list, safe=False)


@login_required
def get_program_schedules(request):
    if request.method == 'GET':
        zone_id = request.GET['zone_id']
    zone = Zone.objects.get(pk=zone_id)
    ps_list = [(x.id, str(x)) for x in ProgramSchedule.objects.filter(center__zone=zone)]
    return JsonResponse(ps_list, safe=False)


@login_required
def get_brochure_image(request):
    if request.method == 'GET':
        brochure_ids = json.loads(request.GET['brochure_ids'])
        ps_list = [(x.id, "%s/%s/%s" % (settings.MEDIA_URL, 'brochure_image',
                                        str(x.brochure_image.file if x.brochure_image else 'no-photo.jpg')[
                                        str(x.brochure_image.file).rfind(
                                            '\\') + 1:] if x.brochure_image else 'no-photo.jpg')) for x in
                   BrochureMaster.objects.filter(pk__in=brochure_ids)]
    return JsonResponse(ps_list, safe=False)
