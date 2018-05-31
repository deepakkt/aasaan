import json

from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.utils.text import slugify
from django.contrib.postgres.fields import JSONField

# Create your models here.


class SmartModel(models.Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # setup a function to give expanded status values
        # instead of the short code stored in database
        self.display_func = lambda x: 'get_' + x + '_display'

        # store old values of following fields to track changes
        self.old_field_list = ['__old_' + x.name for x in self._meta.fields]
        self.field_list = [x.name for x in self._meta.fields]

        self.reset_changed_values()

    # set __old_* fields to current model fields
    # use it for first time init or after comparisons for
    # changes and actions are all done
    def reset_changed_values(self):
        for each_field in self.field_list:
            try:
                setattr(self, '__old_' + each_field, getattr(self, self.display_func(each_field))())
            except (AttributeError, ObjectDoesNotExist):
                try:
                    setattr(self, '__old_' + each_field, str(getattr(self, each_field)))
                except:
                    setattr(self, '__old_' + each_field, None)


    # return a dictionary of changed fields alone
    # along with a tuple of old versus new values
    def changed_fields(self):
        changed_fields = {}
        for old_field, new_field in zip(self.old_field_list, self.field_list):
            try:
                new_field_value = getattr(self, self.display_func(new_field))()
            except AttributeError:
                new_field_value = str(getattr(self, new_field))
            old_field_value = getattr(self, old_field)

            if new_field_value != getattr(self, old_field):
                changed_fields[new_field] = (old_field_value,
                                             new_field_value)
        return changed_fields

    class Meta:
        abstract = True


class NotifyModel(SmartModel):
    notify_toggle = models.BooleanField(default=False)
    notify_meta = JSONField(default="")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_notify_meta(self):
        _notify_fields = self.__class__.NotifyMeta.notify_fields
        changed_fields = self.changed_fields()

        _notify_toggle = False
        _notify_changed_fields = json.loads(self.notify_meta) if self.notify_meta else dict()

        _valid_notifiers = list(set.intersection(set(_notify_fields),
                                                set(changed_fields.keys())))

        if _valid_notifiers:                        
            for _notifier in _valid_notifiers:
                _notify_changed_fields[_notifier] = changed_fields[_notifier]

            _notify_toggle = True

        return (_notify_toggle, _notify_changed_fields)

    def save(self, *args, **kwargs):
        self.notify_toggle, _notify_meta = self.get_notify_meta()
        self.notify_meta = json.dumps(_notify_meta)

        if not self.id:
            try:
                _notify_creation = self.__class__.NotifyMeta.notify_creation
            except AttributeError:
                _notify_creation = False

            if not _notify_creation:
                self.notify_toggle = False
                self.notify_meta = ""
            else:
                _notify_meta['created'] = True
                self.notify_meta = json.dumps(_notify_meta)

        super().save(*args, **kwargs)

    class Meta:
        abstract = True

    class NotifyMeta:
        # child class should override this with 
        # fields it should toggle for notification

        # add field names to this list for notification
        notify_fields = []

        # if no records are created, does notification apply?
        notify_creation = False

        # include instance specific recipients, if applicable
        def get_recipients(self):
            # always return a list
            return []


class Configuration(models.Model):
    configuration_key = models.CharField(max_length=100, unique=True)
    configuration_value = models.TextField()
    configuration_description = models.TextField("a brief description of this setting", blank=True)

    def __str__(self):
        return self.configuration_key

    def save(self, *args, **kwargs):
        self.configuration_key = self.configuration_key.upper().rstrip()
        super(Configuration, self).save(*args, **kwargs)

    class Meta:
        ordering = ['configuration_key']


def get_configuration(key):
    try:
        x = Configuration.objects.get(configuration_key=key)
        return x.configuration_value
    except:
        return ""


def get_configurations(key_prefix):
    return dict(((x.configuration_key, x.configuration_value)
            for x in Configuration.objects.filter(configuration_key__startswith=key_prefix)))
        

class Tag(NotifyModel):
    tag_name = models.CharField(max_length=50, unique=True)

    class Meta:
        ordering = ['tag_name']

    def __str__(self):
        return self.tag_name

    def save(self, *args, **kwargs):
        self.tag_name = slugify(self.tag_name.strip().lower())
        super().save(*args, **kwargs)
        self.reset_changed_values()


    class NotifyMeta:
        notify_fields = ['tag_name']
        notify_creation = False

        def get_recipients(self):
            # always return a list
            return ['Thamu|ipc.itsupport@ishafoundation.org',
                    'Anand|anand.subramanian@ishafoundation.org']
        

class AdminQuery(models.Model):
    query_status = models.CharField(max_length=2, choices=(('RQ', 'Requested'),
                                                            ('AP', 'Approved'),
                                                            ('CO', 'Completed'),
                                                            ('FA', 'Failed')),
                                    default='RQ')
    query_title = models.CharField(max_length=50)
    query = models.TextField()
    query_result = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    executed = models.DateTimeField(null=True)


class MasterDeploy(models.Model):
    deploy_status = models.CharField(max_length=2, choices=(('ST', 'Staged'),
                                                            ('CO', 'Completed'),
                                                            ('FA', 'Failed')),
                                    default='ST')
    commit_title = models.CharField(max_length=50)                                    
    deploy_result = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    executed = models.DateTimeField(null=True)
    

class DatabaseRefresh(models.Model):
    refresh_status = models.CharField(max_length=2, choices=(('ST', 'Staged'),
                                                            ('SU', 'Success'),
                                                            ('BF', 'Backup Failed'),
                                                            ('SF', 'Sync Failed')),
                                    default='ST')
    created = models.DateTimeField(auto_now_add=True)
    executed = models.DateTimeField(null=True)

