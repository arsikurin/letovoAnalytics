import functools as ft
import typing
from zoneinfo import ZoneInfo

import orjson

try:
    # set environment variables if on local machine
    from debug import include_secrets

    include_secrets()
except ImportError:
    include_secrets = typing.Any
from pydantic import BaseSettings, HttpUrl, PostgresDsn, BaseConfig

# fpath = os.path.join(os.path.dirname(__file__), 'utils')
# sys.path.append(fpath)
BaseConfig.json_loads = orjson.loads
BaseConfig.json_dumps = orjson.dumps


class AppSettings(BaseSettings):
    EPS: float = 2.220446049250313e-16
    URL_MAIN_LETOVO: HttpUrl = "https://s.letovo.ru"
    URL_MAIN_API: HttpUrl = "https://letovo-analytics-api.herokuapp.com/"
    URL_MAIN_LOCAL: HttpUrl = "https://letovo-analytics.web.app/"
    URL_LOGIN_LOCAL: HttpUrl = "https://letovo-analytics.web.app/login"
    URL_LOGIN_LETOVO: HttpUrl = "https://s-api.letovo.ru/api/login"
    GOOGLE_FS_KEY: str
    GOOGLE_API_KEY: str
    TG_API_ID: int
    TG_API_HASH: str
    TG_BOT_TOKEN: str
    DATABASE_URL: PostgresDsn
    WEB_CONCURRENCY: int = 4
    PORT: int = 8084
    debug: bool = False
    title: str = "Letovo Analytics Bot API"
    favicon_path: str = "app/static/images/icons/api-icon.png"
    timezone: ZoneInfo = ZoneInfo("Europe/Moscow")

    class Config:
        # validate_assignment
        ...


@ft.cache
def settings() -> AppSettings:
    """
    `settings.cache_clear()` if wanna dump cache
    """
    return AppSettings()
