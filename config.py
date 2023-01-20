import os
from functools import cache
from zoneinfo import ZoneInfo

import orjson
from pydantic import BaseSettings, HttpUrl, PostgresDsn, BaseConfig

BaseConfig.json_loads = orjson.loads
BaseConfig.json_dumps = orjson.dumps


class AppSettings(BaseSettings):
    EPS: float = 2.220446049250313e-16
    URL_MAIN_LETOVO: HttpUrl = "https://s.letovo.ru"
    URL_MAIN_API: HttpUrl = "https://letovo-analytics-api.herokuapp.com"
    URL_MAIN_LOCAL: HttpUrl = "https://arsikur.in"
    URL_LOGIN_LETOVO: HttpUrl = "https://s-api.letovo.ru/api/login"
    URL_LOGIN_LOCAL: HttpUrl = "https://arsikur.in/login"
    GOOGLE_FS_KEY: str
    GOOGLE_API_KEY: str
    TG_API_ID: int
    TG_API_HASH: str
    TG_BOT_TOKEN: str
    TG_BOT_TOKEN_INLINE: str
    DATABASE_URL: PostgresDsn
    CONCURRENCY: int = min(32, (os.cpu_count() or 1) + 4)
    PORT: int = 8084
    production: bool = True
    title_api: str = "Letovo Analytics Bot API"
    timezone: ZoneInfo = ZoneInfo("Europe/Moscow")

    class Config:
        env_file = ".env.development.local"
        env_file_encoding = "utf-8"
        # validate_assignment


@cache
def settings() -> AppSettings:
    """
    ``settings.cache_clear()`` to dump cache
    """
    return AppSettings()
