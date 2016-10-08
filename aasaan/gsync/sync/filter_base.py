__author__ = 'dpack'


class SyncMeta(type):
    """
    This metaclass setups a filter chaining mechanism to apply for database rows
    fetched for sync.
    """
    def __init__(cls, name, bases, attrs):
        # check if this class has a filters attribute
        if not hasattr(cls, 'filters'):
            # it does not which means this is first in the inheritance chain
            # so setup a filter
            cls.filters = []
        else:
            # further down in the chain. So append this class to filters
            cls.filters.append(cls)


class ContactSync(metaclass=SyncMeta):
    """
    Classes that inherit from this class need to implement a
    filter_row method. It needs to take in an iterable and
    return a result tuple after the respective filter logic.

    Example:
    The below is a silly example where it returns a copy of the
    incoming row
    def filter_row(row):
        return tuple(row[:])
    """


class ScheduleSync(metaclass=SyncMeta):
    """
    Classes that inherit from this class need to implement a
    filter_row method. It needs to take in an iterable and
    return a result tuple after the respective filter logic.

    Example:
    The below is a silly example where it returns a copy of the
    incoming row
    def filter_row(row, model_row_instance):
        return tuple(row[:])
    """


class ScheduleEnrollmentSync(metaclass=SyncMeta):
    """
    Classes that inherit from this class need to implement a
    filter_row method. It needs to take in an iterable and
    return a result tuple after the respective filter logic.

    Example:
    The below is a silly example where it returns a copy of the
    incoming row
    def filter_row(row, model_row_instance):
        return tuple(row[:])
    """
