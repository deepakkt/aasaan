import json

from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.utils.text import slugify
from django.contrib.postgres.fields import JSONField

# Create your models here.


class SmartModel(models.Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def display_func(self, x):
        # setup a function to give expanded status values
        # instead of the short code stored in database
        return 'get_' + x + '_display'


    def _get_field_value(self, field_name):
        _display_func = self.display_func(field_name)

        try:
            _display_func_ref = getattr(self, _display_func)
        except:
            _display_func_ref = None

        if _display_func_ref:
            return str(_display_func_ref())

        try:
            return str(getattr(self, field_name))
        except:
            return ""

    # return a dictionary of changed fields alone
    # along with a tuple of old versus new values
    def changed_fields(self):
        changes = dict()
        fields = [_x.name for _x in self._meta.fields]
        _base_values = {
                _x: ("", self._get_field_value(_x)) for _x in fields
            }

        if not self.id:
            return _base_values

        try:
            _old_obj = self.__class__.objects.get(pk=self.id)
        except:
            return _base_values

        _old_values = [_old_obj._get_field_value(_x) for _x in fields]
        _new_values = [self._get_field_value(_x) for _x in fields]
        _value_map = dict(zip(fields, zip(_old_values, _new_values)))
        return {
            _x: _value_map[_x] for _x in _value_map
            if _value_map[_x][0] != _value_map[_x][1]
            }

    def presave(self, *args, **kwargs):
        pass


    def save(self, *args, **kwargs):
        self.presave(*args, **kwargs)
        super().save(*args, **kwargs)
    

    class Meta:
        abstract = True


class NotifyModel(SmartModel):
    notify_toggle = models.BooleanField(default=False)
    notify_meta = JSONField(default="{}")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def get_notify_properties(cls):
        _result = {
            "notify": False,
            "notify_fields": [],
            "notify_creation": False,
            "notify_recipients": False
        }

        try:
            notify_fields = cls.NotifyMeta.notify_fields
        except AttributeError:
            return dict(_result)

        if not notify_fields:
            return dict(_result)

        _result["notify_fields"] = notify_fields[:]
        _result["notify"] = True

        try:
            notify_creation = cls.NotifyMeta.notify_creation
            notify_creation = bool(notify_creation)
        except AttributeError:
            notify_creation = False

        try:
            supplementary = cls.NotifyMeta.get_recipients
            notify_recipients = True
        except AttributeError:
            notify_recipients = False

        _result["notify_creation"] = notify_creation
        _result["notify_recipients"] = notify_recipients

        return _result        

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


    def presave(self, *args, **kwargs):
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


def get_configuration(key, json_config=False):
    try:
        x = Configuration.objects.get(configuration_key=key)

        if json_config:
            return json.loads(x.configuration_value)
        else:
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


    class NotifyMeta:
        notify_fields = ['tag_name']
        notify_creation = False

        def get_recipients(self):
            # always return a list
            return ['Thamu|ipc.itsupport@ishafoundation.org',
                    'Anand|anand.subramanian@ishafoundation.org']
        

class AdminQuery(NotifyModel):
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

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
    
    class NotifyMeta:
        notify_fields = ['query_status']
        notify_creation = True


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

