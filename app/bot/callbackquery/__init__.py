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
    """
    Class for dealing with callback query messages

    Args:
        session (aiohttp.ClientSession): an instance of `TelegramClient` with credentials filled in
        session (aiohttp.ClientSession): an instance of `aiohttp.ClientSession`
        db (Postgresql): connection to the database with users' usage analytics
        fs (Firestore): connection to the database with users' credentials

    Methods:
        # TODO add docs
    """
