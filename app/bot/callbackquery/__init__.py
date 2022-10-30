#  Made by arsikurin in 2022.

from .core import CBQCore
from .dev import CBQueryDev
from .homework import CBQHomework
from .marks import CBQMarks
from .others import CBQOthers
from .schedule import CBQSchedule


class CallbackQuery(
    CBQCore,
    CBQSchedule,
    CBQHomework,
    CBQMarks,
    CBQOthers,
    CBQueryDev
):
    pass
