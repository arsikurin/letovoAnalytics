import functools as ft
import typing

try:
    from debug import include_secrets

    include_secrets()
except ImportError:
    include_secrets = typing.Any
from pydantic import BaseSettings

# import os
# import sys
# fpath = os.path.join(os.path.dirname(__file__), 'utils')
# sys.path.append(fpath)
"""
 --loop [auto|asyncio|uvloop]    Event loop implementation.  [default: auto]
  --http [auto|h11|httptools]     HTTP protocol implementation.  [default:
                                  auto]
  --ws [auto|none|websockets|wsproto]
                                  WebSocket protocol implementation.

"""


class AppSettings(BaseSettings):
    EPS: float = 2.220446049250313e-16
    URL_MAIN_LETOVO: str = "https://s.letovo.ru"
    URL_MAIN_API: str = "https://letovo-analytics-api.herokuapp.com/"
    URL_MAIN_LOCAL: str = "https://letovo-analytics.web.app/"
    URL_LOGIN_LOCAL: str = "https://letovo-analytics.web.app/login"
    URL_LOGIN_LETOVO: str = "https://s-api.letovo.ru/api/login"
    GOOGLE_FS_KEY: str
    GOOGLE_API_KEY: str
    TG_API_ID: int
    TG_API_HASH: str
    TG_BOT_TOKEN: str
    SQL_HOST: str
    SQL_PORT: int = 5432
    SQL_USER: str
    SQL_DBNAME: str
    SQL_PASSWORD: str
    debug: bool = True
    title: str = "Letovo Analytics Bot API"

    class Config:
        # validate_assignment
        ...


@ft.cache
def settings() -> AppSettings:
    """
    `settings.cache_clear()` if wanna dump cache
    """
    return AppSettings()
