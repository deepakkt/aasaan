from schedulemaster.models import ProgramSchedule
from contacts.models import Zone, IndividualRole
from tastypie.resources import ModelResource
from tastypie.authentication import BasicAuthentication, ApiKeyAuthentication
from tastypie.cache import SimpleCache

class ScheduleResource(ModelResource):
    class Meta:
        queryset =  ProgramSchedule.objects.filter(hidden=False,program__admin=False).exclude(status='CA')
        fields = ['start_date', 'end_date',
                'event_management_code', 
                'online_registration_code', 'id',
                'contact_name', 'contact_phone1', 
                'contact_email', 'gender']
        authentication = ApiKeyAuthentication()
        cache = SimpleCache(timeout=10)

    def dehydrate(self, bundle):
        bundle.data['tally_name'] = bundle.obj.tally_name
        bundle.data['program_name'] = bundle.obj.program_name
        bundle.data['center_name'] = bundle.obj.center.center_name
        bundle.data['zone_name'] = bundle.obj.center.zone.zone_name
        bundle.data['schedule_long_name'] = str(bundle.obj)
        return bundle


class ZoneResource(ModelResource):
    class Meta:
        queryset = Zone.objects.all()

        fields = ['zone_name']
        authentication = ApiKeyAuthentication()
        cache = SimpleCache(timeout=10)


    def dehydrate(self, bundle):
        bundle.data['centers'] = [center.center_name for center 
                                    in bundle.obj.centers]
        return bundle


class RoleResource(ModelResource):
    class Meta:
        queryset = IndividualRole.objects.filter(active=True, admin_role=False)

        fields = ['role_name']
        authentication = ApiKeyAuthentication()
        cache = SimpleCache(timeout=10)

    def dehydrate(self, bundle):
        bundle.data['role_level'] = bundle.obj.get_role_level_display()    
        return bundle