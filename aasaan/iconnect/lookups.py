from ajax_select import LookupChannel
from django.utils.html import escape
from django.db.models import Q
from django.utils.six import text_type
import ajax_select
from contacts.models import Contact

@ajax_select.register('cliche')
class ContactLookup(LookupChannel):
    model = Contact

    def get_query(self, q, request):
        return Contact.objects.filter(Q(first_name__icontains=q) | Q(primary_email__istartswith=q)).order_by('first_name')

    def get_result(self, obj):
        """ result is the simple text that is the completion of what the person typed """
        return obj.first_name

    def format_match(self, obj):
        """ (HTML) formatted item for display in the dropdown """
        return "%s<div><i>%s</i></div>" % (escape(obj.first_name), escape(obj.primary_email))
        # return self.format_item_display(obj)

    def format_item_display(self, obj):
        """ (HTML) formatted item for displaying item in the selected deck area """
        return "%s<div><i>%s</i></div>" % (escape(obj.first_name), escape(obj.primary_email))

