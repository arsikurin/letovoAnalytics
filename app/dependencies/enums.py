import re
from enum import Enum


class MarkTypes(Enum):
    RECENT = 1
    SUMMATIVE = 2
    FINAL = 3
    ALL = -10


class Weekdays(Enum):
    Monday = 1
    Tuesday = 2
    Wednesday = 3
    Thursday = 4
    Friday = 5
    Saturday = 6
    SundayHW = 7
    Sunday = 0
    ALL = -10


class PatternMatching:
    def __init__(self, s):
        self.today = bool(re.match(r"to", s))
        self.next = bool(re.match(r"ne", s))
        self.monday = bool(re.match(r"mo", s))
        self.tuesday = bool(re.match(r"tu", s))
        self.wednesday = bool(re.match(r"we", s))
        self.thursday = bool(re.match(r"th", s))
        self.friday = bool(re.match(r"fr", s))
        self.saturday = bool(re.match(r"sa", s))
        self.entire = bool(re.match(r"en", s))
