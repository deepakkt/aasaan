# Older syncs which are not being used anymore
# retaining them here since the logic might be useful for future

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


def sync_siy_dec_2016():
    gc = authenticate()
    SIYDec2016Sync(gc, SIY_DEC_2016_SHEET_KEY).sync()