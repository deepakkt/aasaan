from django.contrib import admin
from .models import FeedbackNotes, Feedback
from django.utils import timezone
from utils.filters import RelatedDropdownFilter
from AasaanUser.models import AasaanUserContact, AasaanUserZone
from django.contrib.auth.models import User
from django.contrib import messages


class FeedbackNotesInline(admin.StackedInline):
    model = FeedbackNotes
    extra = 1
    fields = ['note', ]

    def has_change_permission(self, request, obj=None):
        return False


class FeedbackNotesInline1(admin.StackedInline):

    model = FeedbackNotes
    extra = 0
    readonly_fields = ['note',]

    fieldsets = [
        ('', {'fields': ('note',), }),
        ('Hidden Fields',
         {'fields': ['created_by',], 'classes': ['hidden']}),
    ]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class FeedbackAdmin(admin.ModelAdmin):
    inlines = [FeedbackNotesInline1, FeedbackNotesInline]
    list_display = ('title', 'zone', 'created', 'created_by', 'status')
    list_display_links = ['title']
    list_filter = ('created', ('zone', RelatedDropdownFilter),)

    fieldsets = (
        ('', {
            'fields': ('title', 'status'),
        }),
    )

    def get_form(self, request, obj=None, **kwargs):
        login_user = User.objects.get(username=request.user.username)
        try:
            AasaanUserContact.objects.get(user=login_user)
        except AasaanUserContact.DoesNotExist:
            self.message_user(request,
                              "Contact is not mapped to User. Contact aasaan admin",
                              level=messages.WARNING)
        try:
            AasaanUserZone.objects.get(user=login_user)
        except AasaanUserZone.DoesNotExist:
            self.message_user(request,
                              "Zone is not mapped to User. Contact aasaan admin",
                              level=messages.WARNING)

        return super(FeedbackAdmin, self).get_form(request, obj=None, **kwargs)

    def save_related(self, request, form, formsets, change):
        for formset in formsets:
            for fs in formset:
                if isinstance(fs.instance, FeedbackNotes) and fs.cleaned_data:
                    if fs.instance.pk is None:
                        fs.instance.feedback = form.instance
                        fs.instance.created_by = request.user.username
                        fs.instance.note = fs.instance.note + '\n -- created_by : ' + request.user.username + ' created at : ' + timezone.now().strftime(
                            "%b %d %Y %H:%M:%S")
                        fs.instance.save()
        super(FeedbackAdmin, self).save_related(request, form, formsets, change)

    def save_model(self, request, obj, form, change):
        login_user = User.objects.get(username=request.user.username)
        zone = AasaanUserZone.objects.get(user=login_user)
        obj.zone = zone.zone
        obj.created_by = request.user
        obj.save()

    def get_actions(self, request):
        actions = super(FeedbackAdmin, self).get_actions(request)
        if request.user.is_superuser:
            return actions
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def get_list_filter(self, request):
        filters = super(FeedbackAdmin, self).get_list_filter(request)
        if request.user.is_superuser:
            return filters
        filters = []
        return filters

    def get_queryset(self, request):
        qs = super(FeedbackAdmin, self).get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(created_by=request.user)

    class Media:
        js = ('/static/aasaan/feedback/feedback.js',)

admin.site.register(Feedback, FeedbackAdmin)