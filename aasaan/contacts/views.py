from django.shortcuts import render
from django.views.generic import ListView

from .models import Contact,Zone, IndividualRole, IndividualContactRoleZone, IndividualContactRoleCenter
from django.views.generic import TemplateView
from django.http import JsonResponse
from braces.views import LoginRequiredMixin
from .forms import FilterFieldsForm


class ListContactView(ListView):
    model = Contact
    template_name = 'contacts/contacts_list.html'


class ContactSummaryDashboard(LoginRequiredMixin, TemplateView):
    template = "contacts/summary.html"
    template_name = "contacts/summary.html"
    login_url = "/admin/login/?next=/"

    def get(self, request):
        form = FilterFieldsForm()
        return render(request, self.template, {'form': form})


def s_refresh(request):
    zone = request.GET['zone']
    roles = request.GET['roles']
    if request.user.is_superuser and  zone != 'null':
        if (zone.find(',') > 0):
            zs = zone.split(',')
        else:
            zs = [zone, ]
        z = list(Zone.objects.filter(pk__in=zs))
        contact_zones = Contact.objects.filter(individualcontactrolezone__zone__in=z)
        contact_center_zones = Contact.objects.filter(individualcontactrolecenter__center__zone__in=z)
        contact_zones = contact_zones | contact_center_zones
        contact_zones = contact_zones.distinct()
    elif request.user.is_superuser and zone == 'null':
        contact_zones = Contact.objects.all()
    else:
        # get all centers this user belongs to
        user_centers = [x.center for x in request.user.aasaanusercenter_set.all()]
        user_zones = [x.zone for x in request.user.aasaanuserzone_set.all()]
        print(user_zones)

        # get all contacts who have a role in above user's centers
        center_contacts = Contact.objects.filter(individualcontactrolecenter__center__in=user_centers)

        # contacts may belong to centers which belong to zones above user has permission for. get those too
        center_zonal_contacts = Contact.objects.filter(individualcontactrolecenter__center__zone__in=user_zones)

        # finally directly get contacts belonging to zone the user has access to
        zone_contacts = Contact.objects.filter(individualcontactrolezone__zone__in=user_zones)

        print(zone_contacts)

        # merge all of them
        all_contacts = center_contacts | zone_contacts | center_zonal_contacts
        # and de-dupe them!
        contact_zones = all_contacts.distinct()

    if roles == 'null':
        pass
    else:
        if roles.find(',')>0:
            rs = roles.split(',')
        else:
            rs=[roles,]

        ivz = contact_zones.filter(individualcontactrolezone__role__in=IndividualRole.objects.filter(pk__in=rs))
        ivc = contact_zones.filter(individualcontactrolecenter__role__in=IndividualRole.objects.filter(pk__in=rs))
        iv = ivz.distinct() | ivc.distinct()
        contact_zones = iv.distinct()

    summary = { }
    # summary['draw'] = 25
    # summary['recordsTotal'] = 1000
    # summary['recordsFiltered'] = 1000
    data = []
    for c in contact_zones:
        icrz = IndividualContactRoleZone.objects.filter(contact=c)
        z_role_list = [x.role.role_name for x in icrz]
        z_zone_list = [x.zone.zone_name for x in icrz]
        icrc = IndividualContactRoleCenter.objects.filter(contact=c)
        c_role_list = [x.role.role_name for x in icrc]
        c_zone_list = [x.center.zone.zone_name for x in icrc]
        center_list = list(set([x.center.center_name for x in icrc]))
        role_list = list(set(z_role_list + c_role_list))
        zone_list = list(set(z_zone_list + c_zone_list))
        data.append({'id':c.pk, 'name':c.full_name, 'gender':c.get_gender_display(), 'category':c.get_category_display(), 'primary_email':c.primary_email, 'phone_number':c.primary_mobile, 'zone':zone_list, 'center':center_list, 'roles':role_list})
    summary['data'] = data
    return JsonResponse( summary , safe=False)


