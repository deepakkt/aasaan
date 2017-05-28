from datetime import datetime, date
import json
import pickle
from tempfile import NamedTemporaryFile as NTF

from django.core.exceptions import ImproperlyConfigured

from schedulemaster.models import ProgramSchedule, ProgramCountMaster
from contacts.models import IndividualContactRoleCenter, \
    IndividualContactRoleZone, Center

from .sheets_api import open_workbook, delete_worksheets, update_header_row, \
    update_cell, update_row, authenticate

from .settings import schedule_sync_rows, contact_sync_rows, schedule_enrollment_sync_rows, \
    CONTACTS_SHEET_KEY, \
    schedule_header, contact_header, schedule_enrollment_header, \
    SCHEDULE_SHEET_KEY, SCHEDULE_SHEET_KEY_TEST, \
    CONTACTS_SHEET_KEY_TEST, SCHEDULE_ENROLLMENT_SHEET_KEY, \
    enrollment_count_categories, siy_dec2016_sync_rows, siy_dec_2016_header,\
    SIY_DEC_2016_SHEET_KEY, SCHEDULE_IYC_SHEET_KEY

from . import contact_filter, schedule_filter, schedule_enrollment_filter

from config.ors.ors import ORSInterface
from django.conf import settings


class SheetSync:
    """
    This class is the root of a sync operation. If you're inheriting from this, define the following
    a models parameter with the list of models
    titles which take column titles for the spreadsheet
    sheet_key which is the spreadsheet id
    pivot_fields - a list of field names corresponding to the column on which the sheets are to be split
    filters - a class that inherits from SyncMeta with a list of filters
    target_columns - a list of named tuples for the target value list

    The inheritor must implement a translate_<modelname> method which will return a list of values
    that will make up the spreadsheet row
    The inheritor can optionally implement a get_<modelname>_queryset method which will return the
    queryset for the model. It is highly recommended to implement this the class will return a
    model.objects.all() queryset otherwise
    """

    # list all the models that will be used for syncing
    models = []
    # fields from each model to be given here
    titles = []
    # pivot fields is one field per model which
    # will be used to split the row base into
    # individual sheets
    pivot_fields = []
    # for multi-models, if the columns are the same
    # include the same namedtuple
    target_columns = []
    # If there are no filters for a model, issue None
    filters = []

    def __init__(self, gc, sheet_key=""):
        # get a reference to the authentication backend
        # if one doesn't exist, create it
        self.gc = gc or authenticate()
        self.__class__.sheet_key = sheet_key

        self.model_map = dict()
        self.pivot_map = dict()

        # the upcoming section setups up a dictionary for the model
        # that gives all sync related tools for a given model
        model_parms = {'queryset': None, 'translate': None,
                       'pivot': None, 'namedtuple': None,
                       'model': None, 'filters': None}

        for model, pivot, columns, filters in zip(self.__class__.models,
                                         self.__class__.pivot_fields,
                                         self.__class__.target_columns,
                                            self.__class__.filters):
            model_name = model.__name__
            self.model_map[model_name] = dict(model_parms)
            self.model_map[model_name]['model'] = model
            self.model_map[model_name]['pivot'] = pivot
            self.model_map[model_name]['namedtuple'] = columns
            self.model_map[model_name]['filters'] = filters

            # see if an overriding get_<model_name>_queryset method is implemented
            # in the class. If so, use that. Else use the <model_name>.objects.all()
            # queryset
            self.model_map[model_name]['queryset'] = getattr(self, 'get_' + model_name.lower() +
                                                             '_queryset')() if \
                hasattr(self, 'get_' + model_name.lower() + '_queryset') \
                else model.objects.all()

            # the class *must* implement a translate_<model_name> method. Throw an error
            # if not
            try:
                self.model_map[model_name]['translate'] = getattr(self, 'translate_' + model_name.lower())
            except NameError:
                raise ImproperlyConfigured('class %s or one of its parents must implement the '
                                           '%s method. The method is missing.' %(self.__class__.__name__,
                                                                                 'translate_' + model_name.lower()))

        if len(self.__class__.models) != len(list(self.model_map.keys())):
            print(len(self.__class__.models))
            print(len(list(self.model_map.keys())))
            raise ImproperlyConfigured('class %s seems to inconsistently define model tools.'
                                       'Check if pivot fields, filters, named tuples and '
                                       'target columns all map with corresponding models. Define'
                                       'them with None if they are not implemented or required'
                                       %(self.__class__.__name__))

        # obtain reference to workbook
        self.workbook = open_workbook(spreadsheet_key=self.__class__.sheet_key,
                                      gc_interface=self.gc)

        # and delete worksheets in the workbook
        delete_worksheets(self.workbook)

    def filter(self, instance, values_list, filters):
        result = values_list._make(values_list)
        for each_filter in filters.filters:
            result = each_filter.filter_row(result, instance)
        return result

    def sync(self):
        _worksheet = -1
        _worksheet_row = 0
        _worksheet_start_row = 2
        _worksheet_columns = 30

        for model in self.model_map:
            for instance in self.model_map[model]['queryset']:
                result = self.model_map[model]['translate'](instance)
                if self.model_map[model]['filters']:
                    result = self.filter(instance, result, self.model_map[model]['filters'])

                if not result:
                    continue

                try:
                    pivot_value = eval('result.' + self.model_map[model]['pivot']) if self.model_map[model]['pivot'] else 'main'
                except AttributeError:
                    raise ImproperlyConfigured('class %s specifies a pivot field of %s.'
                                               'The %s method however does not return this field.'
                                               % (self.__class__.__name__,
                                                   self.model_map[model]['pivot'],
                                                  self.model_map[model]['translate']))

                # check if this pivot value already has an entry. If not, create a new sheet
                # and map it
                if not self.pivot_map.get(pivot_value):
                    self.pivot_map[pivot_value] = [_worksheet_start_row, self.workbook.add_worksheet(pivot_value, 1000, _worksheet_columns)]
                    update_header_row(self.pivot_map[pivot_value][_worksheet],
                                      values_list=self.__class__.titles)

                # replace the default '0' for serial number with one in our pivot map
                result = result._make((self.pivot_map[pivot_value][_worksheet_row] - 1,) +
                                      result[1:])

                update_row(worksheet=self.pivot_map[pivot_value][_worksheet],
                           start_row=self.pivot_map[pivot_value][_worksheet_row],
                           start_col=1,
                           values_list=tuple(result))

                self.pivot_map[pivot_value][_worksheet_row] += 1

        last_synced = 'Last synced: ' + datetime.now().isoformat()
        update_cell(self.workbook.worksheet("Reference"), "A1", last_synced)


class SheetSyncCache(SheetSync):        
    """
    Functionality is similar to SheetSync. Except that all records fetched are cached
    to a temporary file prior to working with gspread sheets.
    This should avoid connection errors with Google Sheets because latency involved
    with database are separated out
    """

    def sync(self):
        _worksheet = -1
        _worksheet_row = 0
        _worksheet_start_row = 2
        _worksheet_columns = 30
        
        for model in self.model_map:
            tempfile = NTF()
            print("tempfile ==> ", tempfile.name)
            for instance in self.model_map[model]['queryset']:
                result = self.model_map[model]['translate'](instance)
                if self.model_map[model]['filters']:
                    result = self.filter(instance, result, self.model_map[model]['filters'])

                if not result:
                    continue

                pickle.dump(tuple(result), tempfile)

            last_result = result

            tempfile.seek(0)
            while 1:
                try:
                    result = pickle.load(tempfile)
                    result = last_result._make(result)
                except EOFError:
                    break

                try:
                    pivot_value = eval('result.' + self.model_map[model]['pivot']) if self.model_map[model]['pivot'] else 'main'
                except AttributeError:
                    raise ImproperlyConfigured('class %s specifies a pivot field of %s.'
                                               'The %s method however does not return this field.'
                                               % (self.__class__.__name__,
                                                   self.model_map[model]['pivot'],
                                                  self.model_map[model]['translate']))

                # check if this pivot value already has an entry. If not, create a new sheet
                # and map it
                if not self.pivot_map.get(pivot_value):
                    self.pivot_map[pivot_value] = [_worksheet_start_row, self.workbook.add_worksheet(pivot_value, 1000, 26)]
                    update_header_row(self.pivot_map[pivot_value][_worksheet],
                                      values_list=self.__class__.titles)

                # replace the default '0' for serial number with one in our pivot map
                result = result._make((self.pivot_map[pivot_value][_worksheet_row] - 1,) +
                                      result[1:])

                update_row(worksheet=self.pivot_map[pivot_value][_worksheet],
                           start_row=self.pivot_map[pivot_value][_worksheet_row],
                           start_col=1,
                           values_list=tuple(result))

                self.pivot_map[pivot_value][_worksheet_row] += 1
            tempfile.close()

        last_synced = 'Last synced: ' + datetime.now().isoformat()
        update_cell(self.workbook.worksheet("Reference"), "A1", last_synced)


class ScheduleSync(SheetSyncCache):
    models = [ProgramSchedule]
    titles = schedule_sync_rows
    pivot_fields = ['zone']
    target_columns = [schedule_header]
    filters = [schedule_filter.ScheduleSync]

    def get_programschedule_queryset(self):
        forty_five_days_ago = date.fromordinal(date.today().toordinal() - 45)
        return ProgramSchedule.objects.filter(start_date__gte=forty_five_days_ago).order_by('center__zone',
                                                                                            '-start_date',
                                                                                            'center', 'program')
    def translate_programschedule(self, instance):
        _worksheet_row = 0

        months = ['Ignore', 'January', 'February', 'March',
                  'April', 'May', 'June', 'July', 'August',
                  'September', 'October', 'November', 'December']

        # generate program timings in the format of M-N-E
        timing_codes = '-'.join([x.batch.batch_code for x in instance.programbatch_set.all()])
        # get all venues for this program
        schedule_venue = instance.programvenueaddress_set.all()

        _date_fmt = lambda x: "-".join([str(x.day), str(months[x.month][:3]),
                                        str(x.year)])

        # build a value list
        schedule_values = [_worksheet_row,
                           instance.center.zone.zone_name,
                           _date_fmt(instance.start_date),
                           _date_fmt(instance.end_date),
                           instance.center.center_name,
                           instance.center.parent_center.center_name if instance.center.pre_center else "",
                           instance.program_name,
                           timing_codes,
                           instance.get_gender_display(),
                           instance.primary_language.name,
                           instance.get_status_display(),
                            instance.event_management_code,
                            instance.online_registration_code,
                           instance.contact_phone1,
                           instance.contact_email,
                           "" if not schedule_venue else schedule_venue[0].address,
                           instance.id,
                           instance.last_modified]

        return schedule_header(*schedule_values)


class ContactSync(SheetSync):
    models = [IndividualContactRoleZone,
              IndividualContactRoleCenter]
    titles = contact_sync_rows
    pivot_fields = ['zone', 'zone']
    target_columns = [contact_header, contact_header]
    filters = [contact_filter.ContactSync,
               contact_filter.ContactSync]

    def get_individualcontactrolezone_queryset(self):
        return IndividualContactRoleZone.objects.all().order_by('zone', 'role',
                                                                'contact__first_name')

    def get_individualcontactrolecenter_queryset(self):
        return IndividualContactRoleCenter.objects.all().order_by('center__zone', 'center',
                                                                  'role', 'contact__first_name')
    def translate_individualcontactrolezone(self, instance):
        _worksheet_row = 0
        contact_address = instance.contact.contactaddress_set.all()

        contact_values = [_worksheet_row,
                          instance.contact.full_name,
                          instance.contact.primary_mobile,
                          instance.contact.whatsapp_number,
                          instance.contact.primary_email,
                          instance.zone.zone_name,
                          "",
                          instance.role.role_name,
                          "" if not contact_address else contact_address[0].address]

        return contact_header(*contact_values)

    def translate_individualcontactrolecenter(self, instance):
        _worksheet_row = 0
        contact_address = instance.contact.contactaddress_set.all()

        contact_values = [_worksheet_row,
                          instance.contact.full_name,
                          instance.contact.primary_mobile,
                          instance.contact.whatsapp_number,
                          instance.contact.primary_email,
                          instance.center.zone.zone_name,
                          instance.center.center_name,
                          instance.role.role_name,
                          "" if not contact_address else contact_address[0].address]

        return contact_header(*contact_values)


class ScheduleEnrollmentSync(SheetSyncCache):
    models = [ProgramSchedule]
    titles = schedule_enrollment_sync_rows
    pivot_fields = ['zone']
    target_columns = [schedule_enrollment_header]
    filters = [schedule_enrollment_filter.ScheduleEnrollmentSync]

    def __init__(self, *args, **kwargs):
        self._counts_master = enrollment_count_categories
        super().__init__(*args, **kwargs)

    def get_programschedule_queryset(self):
        forty_five_days_ago = date.fromordinal(date.today().toordinal() - 45)
        return ProgramSchedule.objects.filter(start_date__gte=forty_five_days_ago).order_by('center__zone',
                                                                                            '-start_date',
                                                                                            'center', 'program')

    def translate_programschedule(self, instance):
        def _get_category_values():
            program_category_values = [(x.category.count_category, x.value)
                                       for x in instance.programschedulecounts_set.all()]
            program_categories = [x[0] for x in program_category_values]
            category_values = []

            for each_master_category in self._counts_master:
                if each_master_category in program_categories:
                    master_category_index = program_categories.index(each_master_category)
                    category_value = program_category_values[master_category_index][-1]
                    category_values.append(category_value)
                else:
                    category_values.append('')

            return category_values

        _worksheet_row = 0

        months = ['Ignore', 'January', 'February', 'March',
                  'April', 'May', 'June', 'July', 'August',
                  'September', 'October', 'November', 'December']

        # generate program timings in the format of M-N-E
        timing_codes = '-'.join([x.batch.batch_code for x in instance.programbatch_set.all()])

        # get a list of teachers and their roles for this program as a comma separated field
        program_teachers = '\n'.join([t.teacher.full_name + ' - ' + t.get_teacher_type_display()
                            for t in instance.programteacher_set.all()])

        _date_fmt = lambda x: "-".join([str(x.day), str(months[x.month][:3]),
                                        str(x.year)])

        _program_name = lambda: instance.event_name if instance.program.name == "Special Event" else instance.program.name

        # build a value list
        schedule_enrollment_values = [_worksheet_row,
                           instance.center.zone.zone_name,
                           _date_fmt(instance.start_date),
                           _date_fmt(instance.end_date),
                           instance.center.center_name,
                           instance.center.parent_center.center_name if instance.center.pre_center else "",
                           instance.program_name,
                           timing_codes,
                           instance.get_gender_display(),
                           instance.primary_language.name,
                           instance.get_status_display(),
                                      instance.event_management_code,
                           program_teachers]

        schedule_enrollment_values.extend(_get_category_values())
        schedule_enrollment_values.extend([instance.id, instance.last_modified])

        return schedule_enrollment_header(*schedule_enrollment_values)


class IYCScheduleSync(ScheduleSync):
    models = [ProgramSchedule]
    titles = schedule_sync_rows
    pivot_fields = ['zone']
    target_columns = [schedule_header]
    filters = [None]

    def get_programschedule_queryset(self):
        forty_five_days_ago = date.fromordinal(date.today().toordinal() - 45)
        filter_zone = 'Isha Yoga Center'
        return ProgramSchedule.objects.filter(start_date__gte=forty_five_days_ago,
                                              center__zone__zone_name=filter_zone).order_by('-start_date',
                                                                                            'program')


class SIYDec2016Sync(SheetSync):
    models = [ProgramSchedule]
    titles = siy_dec2016_sync_rows
    pivot_fields = [None]
    target_columns = [siy_dec_2016_header]
    filters = [None]

    def __init__(self, *args, **kwargs):
        self.center_map = {x.center_name: x.zone.zone_name for x in Center.objects.all()}
        super().__init__(*args, **kwargs)

    def get_programschedule_queryset(self):
        ors_interface = ORSInterface(settings.ORS_USER, settings.ORS_PASSWORD)
        ors_interface.authenticate()
        program_filter = "ProgramName~substringof~'sadhguruvudan'"
        siy_programs = ors_interface.getprogramlist(postFilterString=program_filter)

        siy_programs_dict = dict(siy_programs)
        _venue = lambda x: x.split('-')[1].strip()

        siy_programs_list = [(z['ProgramID'], _venue(z['ProgramName']),
                              self.center_map[_venue(z['ProgramName'])],
                              1000 - z['SeatAvailability'])
                             for z in siy_programs_dict['data']
                             if (z['ProgramName'].find('17-Dec-2016') > 0 and _venue(z['ProgramName']) != 'Adi Yogi Aalayam')]
        siy_programs_list_dict = {x[1]: x for x in siy_programs_list}
        siy_programs_list_dict_keys = list(siy_programs_list_dict.keys())
        siy_programs_list_dict_keys = sorted(siy_programs_list_dict_keys)
        siy_programs_list = [siy_programs_list_dict[x] for x in siy_programs_list_dict_keys]
        total_enrollment = sum([x[-1] for x in siy_programs_list])
        siy_programs_list.append(('', '', 'Total Enrollment', total_enrollment))
        return siy_programs_list

    def translate_programschedule(self, instance):
        instance_and_sno = (0,) + instance
        return siy_dec_2016_header(*instance_and_sno)


def sync_schedules():
    gc = authenticate()
    ScheduleSync(gc, SCHEDULE_SHEET_KEY).sync()


def sync_schedules_test():
    gc = authenticate()
    ScheduleSync(gc, SCHEDULE_SHEET_KEY_TEST).sync()


def sync_contacts():
    gc = authenticate()
    ContactSync(gc, CONTACTS_SHEET_KEY).sync()


def sync_contacts_test():
    gc = authenticate()
    ContactSync(gc, CONTACTS_SHEET_KEY_TEST).sync()


def sync_enrollments():
    gc = authenticate()
    ScheduleEnrollmentSync(gc, SCHEDULE_ENROLLMENT_SHEET_KEY).sync()


def sync_iyc_schedules():
    gc = authenticate()
    IYCScheduleSync(gc, SCHEDULE_IYC_SHEET_KEY).sync()


def sync_siy_dec_2016():
    gc = authenticate()
    SIYDec2016Sync(gc, SIY_DEC_2016_SHEET_KEY).sync()