from collections import namedtuple
from dataclasses import dataclass

from .enums import MarkTypes, MatchWeekdays, Weekdays, FSData, FSNames

__all__ = (
    "Weekdays",
    "MarkTypes",
    "MatchWeekdays",
    "FSData",
    "FSNames",
    "AnalyticsResponse",
    "Mark",
    "clients"
)


@dataclass(slots=True)
class AnalyticsResponse:
    sender_id: str
    schedule_counter: int
    homework_counter: int
    marks_counter: int
    holidays_counter: int
    clear_counter: int
    options_counter: int
    help_counter: int
    about_counter: int
    inline_counter: int


@dataclass(slots=True)
class Mark:
    criterion: str
    count: int = 0
    sum: int = 0


clients = namedtuple("clients", ["client", "client_i"])
