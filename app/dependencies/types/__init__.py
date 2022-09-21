from collections import namedtuple
from dataclasses import dataclass

from .enums import MarkTypes, MatchWeekdays, Weekdays

__all__ = (
    "Weekdays",
    "MarkTypes",
    "MatchWeekdays",
    "AnalyticsResponse",
    "Clients"
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


Clients = namedtuple("Clients", ["client", "client_i"])
