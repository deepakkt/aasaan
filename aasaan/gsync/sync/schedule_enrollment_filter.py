__author__ = 'dpack'

from .filter_base import ScheduleEnrollmentSync
from .settings import schedule_enrollment_header


class ScheduleFilterHidden(ScheduleEnrollmentSync):
    def filter_row(schedule, schedule_model):
        if not schedule:
            return tuple()

        if schedule_model.hidden:
            return tuple()

        return schedule_enrollment_header(*schedule)


class ScheduleFilterAdmin(ScheduleEnrollmentSync):
    def filter_row(schedule, schedule_model):
        if not schedule:
            return tuple()

        if schedule_model.program.admin:
            return tuple()

        return schedule_enrollment_header(*schedule)


class ScheduleFilterInactive(ScheduleEnrollmentSync):
    def filter_row(schedule, schedule_model):
        if not schedule:
            return tuple()

        if not schedule_model.program.active:
            return tuple()

        return schedule_enrollment_header(*schedule)

