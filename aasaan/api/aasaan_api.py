from schedulemaster.models import ProgramSchedule
from tastypie.resources import ModelResource
from tastypie.authentication import BasicAuthentication, ApiKeyAuthentication
from tastypie.cache import SimpleCache

from utils.datedeux import DateDeux

class ScheduleResource(ModelResource):
    class Meta:
        forty_five_days_ago = DateDeux.today() - 45
        queryset =  ProgramSchedule.objects.filter(hidden=False,program__admin=False)
        fields = ['start_date', 'center',
                'event_management_code', 
                'online_registration_code', 'id']
        authentication = ApiKeyAuthentication()
        cache = SimpleCache(timeout=10)

    def dehydrate(self, bundle):
        bundle.data['tally_name'] = bundle.obj.tally_name
        bundle.data['program_name'] = bundle.obj.program_name
        return bundle