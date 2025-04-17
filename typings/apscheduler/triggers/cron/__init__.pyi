"""
This type stub file was generated by pyright.
"""

from datetime import datetime, timedelta
from tzlocal import get_localzone
from apscheduler.triggers.base import BaseTrigger
from apscheduler.triggers.cron.fields import BaseField, DEFAULT_VALUES, DayOfMonthField, DayOfWeekField, MonthField, WeekField
from apscheduler.util import astimezone, convert_to_datetime, datetime_ceil, datetime_repr

class CronTrigger(BaseTrigger):
    """
    Triggers when current time matches all specified time constraints,
    similarly to how the UNIX cron scheduler works.

    :param int|str year: 4-digit year
    :param int|str month: month (1-12)
    :param int|str day: day of month (1-31)
    :param int|str week: ISO week (1-53)
    :param int|str day_of_week: number or name of weekday (0-6 or mon,tue,wed,thu,fri,sat,sun)
    :param int|str hour: hour (0-23)
    :param int|str minute: minute (0-59)
    :param int|str second: second (0-59)
    :param datetime|str start_date: earliest possible date/time to trigger on (inclusive)
    :param datetime|str end_date: latest possible date/time to trigger on (inclusive)
    :param datetime.tzinfo|str timezone: time zone to use for the date/time calculations (defaults
        to scheduler timezone)
    :param int|None jitter: delay the job execution by ``jitter`` seconds at most

    .. note:: The first weekday is always **monday**.
    """
    FIELD_NAMES = ...
    FIELDS_MAP = ...
    __slots__ = ...
    def __init__(self, year=..., month=..., day=..., week=..., day_of_week=..., hour=..., minute=..., second=..., start_date=..., end_date=..., timezone=..., jitter=...) -> None:
        ...
    
    @classmethod
    def from_crontab(cls, expr, timezone=...): # -> Self:
        """
        Create a :class:`~CronTrigger` from a standard crontab expression.

        See https://en.wikipedia.org/wiki/Cron for more information on the format accepted here.

        :param expr: minute, hour, day of month, month, day of week
        :param datetime.tzinfo|str timezone: time zone to use for the date/time calculations (
            defaults to scheduler timezone)
        :return: a :class:`~CronTrigger` instance

        """
        ...
    
    def get_next_fire_time(self, previous_fire_time, now): # -> None:
        ...
    
    def __getstate__(self): # -> dict[str, Any]:
        ...
    
    def __setstate__(self, state): # -> None:
        ...
    
    def __str__(self) -> str:
        ...
    
    def __repr__(self): # -> str:
        ...
    


