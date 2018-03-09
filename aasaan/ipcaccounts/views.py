import json
from django.contrib.auth.decorators import login_required
from schedulemaster.models import ProgramSchedule, ProgramMaster
from config.models import Configuration
from django.http import JsonResponse
from django.utils import formats
@login_required
def get_budget_code(request):
    if request.method == 'GET':
        program_id = request.GET['program_schedule']
        program_schedule = ProgramSchedule.objects.get(id=program_id)
        program_master = ProgramMaster.objects.get(name=program_schedule.program.name)
        cft = Configuration.objects.get(configuration_key='IPC_ACCOUNTS_TRACKING_CONST')
        data = json.loads(cft.configuration_value)
        prefix = data[program_schedule.center.zone.zone_name]['prefix']
        formatted_start_date = formats.date_format(program_schedule.start_date, "DATE_FORMAT")
        budget_code = prefix+'-'+program_schedule.center.center_name+'-'+program_master.abbreviation+ '-'+formatted_start_date
        return JsonResponse(budget_code, safe=False)