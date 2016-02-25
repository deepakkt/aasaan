from ajax_select import LookupChannel
from django.utils.html import escape
from django.db.models import Q
from django.utils.six import text_type
import ajax_select
from contacts.models import Contact, RoleGroup, IndividualRole, Zone, Center

@ajax_select.register('contact')
class ContactLookup(LookupChannel):
    model = Contact

    def get_query(self, q, request):
        return Contact.objects.filter(Q(first_name__icontains=q) | Q(primary_email__istartswith=q)).order_by('first_name')

    def get_result(self, obj):
        """ result is the simple text that is the completion of what the person typed """
        return obj.first_name+ ' '+ obj.last_name

    def format_match(self, obj):
        """ (HTML) formatted item for display in the dropdown """
        return "%s" % (escape(obj.first_name +' '+ obj.last_name))
        # return self.format_item_display(obj)

    def format_item_display(self, obj):
        """ (HTML) formatted item for displaying item in the selected deck area """
        return "%s" % (escape(obj.first_name +' '+ obj.last_name))


@ajax_select.register('ipc_role_group')
class IPCRolesLookup(LookupChannel):
    model = RoleGroup

    def get_query(self, q, request):
        return RoleGroup.objects.filter(Q(role_name__icontains=q) | Q(role_name__istartswith=q)).order_by('role_name')

    def get_result(self, obj):
        """ result is the simple text that is the completion of what the person typed """
        return obj.role_name

    def format_match(self, obj):
        """ (HTML) formatted item for display in the dropdown """
        return "%s" % (escape(obj.role_name))
        # return self.format_item_display(obj)

    def format_item_display(self, obj):
        """ (HTML) formatted item for displaying item in the selected deck area """
        return "%s" % (escape(obj.role_name))


@ajax_select.register('ipc_role')
class IVRolesLookup(LookupChannel):
    model = IndividualRole

    def get_query(self, q, request):
        return IndividualRole.objects.filter(Q(role_name__icontains=q) | Q(role_name__istartswith=q)).order_by('role_name')

    def get_result(self, obj):
        """ result is the simple text that is the completion of what the person typed """
        return obj.role_name

    def format_match(self, obj):
        """ (HTML) formatted item for display in the dropdown """
        return "%s" % (escape(obj.role_name))
        # return self.format_item_display(obj)

    def format_item_display(self, obj):
        """ (HTML) formatted item for displaying item in the selected deck area """
        return "%s" % (escape(obj.role_name))


@ajax_select.register('zone')
class ZoneLookup(LookupChannel):
    model = Zone

    def get_query(self, q, request):
        return Zone.objects.filter(Q(zone_name__icontains=q) | Q(zone_name__istartswith=q)).order_by('zone_name')

    def get_result(self, obj):
        """ result is the simple text that is the completion of what the person typed """
        return obj.zone_name

    def format_match(self, obj):
        """ (HTML) formatted item for display in the dropdown """
        return "%s" % (escape(obj.zone_name))
        # return self.format_item_display(obj)

    def format_item_display(self, obj):
        """ (HTML) formatted item for displaying item in the selected deck area """
        return "%s" % (escape(obj.zone_name))

@ajax_select.register('center')
class CenterLookup(LookupChannel):
    model = Center

    def get_query(self, q, request):
        return Center.objects.filter(Q(center_name__icontains=q) | Q(center_name__istartswith=q)).order_by('center_name')

    def get_result(self, obj):
        """ result is the simple text that is the completion of what the person typed """
        return obj.center_name

    def format_match(self, obj):
        """ (HTML) formatted item for display in the dropdown """
        return "%s" % (escape(obj.center_name))
        # return self.format_item_display(obj)

    def format_item_display(self, obj):
        """ (HTML) formatted item for displaying item in the selected deck area """
        return "%s" % (escape(obj.center_name))

