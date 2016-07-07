__author__ = 'dpack'

from datetime import date

from .filter_base import ScheduleSync
from .settings import schedule_header


class ScheduleFilterDate(ScheduleSync):
    def filter_row(schedule, schedule_model):
        if not schedule:
            return tuple()

        if schedule_model.end_date < date.fromordinal(date.today().toordinal() - 30):
            return tuple()

        return schedule_header(*schedule)


class ScheduleFilterHidden(ScheduleSync):
    def filter_row(schedule, schedule_model):
        if not schedule:
            return tuple()

        if schedule_model.hidden:
            return tuple()

        return schedule_header(*schedule)


class ScheduleFilterAdmin(ScheduleSync):
    def filter_row(schedule, schedule_model):
        if not schedule:
            return tuple()

        if schedule_model.program.admin:
            return tuple()

        return schedule_header(*schedule)


class ScheduleFilterInactive(ScheduleSync):
    def filter_row(schedule, schedule_model):
        if not schedule:
            return tuple()

        if not schedule_model.program.active:
            return tuple()

        return schedule_header(*schedule)