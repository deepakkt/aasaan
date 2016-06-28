import json
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import BrochureSetItem, Brochures, StockPointMaster


@login_required
def get_brochure_list(request):
    if request.method == 'GET':
        stock_id = request.GET['source_stock_point']
    brochure_list = Brochures.objects.filter(stock_point=StockPointMaster.objects.get(pk__in=stock_id),
                                             status='ACTV').values_list('item', 'quantity')
    return JsonResponse(json.dumps(list(brochure_list)), safe=False)


@login_required
def get_brochure_set(request):
    if request.method == 'GET':
        brochure_set = request.GET['brochure_set']
    brochure_list = BrochureSetItem.objects.filter(brochure_set=brochure_set).values_list('item', 'quantity')
    # dkt - no need to call json.dumps for JsonResponse. Just pass brochure_list
    return JsonResponse(json.dumps(list(brochure_list)), safe=False)
