import asyncio
import datetime
import logging as log
import typing

import aiohttp
import orjson

from app.dependencies import errors as errors_l, types as types_l
from config import settings

if typing.TYPE_CHECKING:
    from app.dependencies import Firestore

creds_not_found_text = "Credentials not found in the database"
no_conn_text = "Cannot establish connection to s.letovo.ru"
too_long_conn_text = "s.letovo.ru takes too long to respond"


@typing.final
class API:
    """
    Class for dealing with web API of s.letovo.ru

    Args:
        session (aiohttp.ClientSession): an instance of `aiohttp.ClientSession`
        fs (Firestore): connection to the database with users' credentials
    """

    __slots__ = ("session", "fs")
    _instance = None

    # def __new__(cls, *args, **kwargs):
    #     if cls._instance is None:
    #         cls._instance = super().__new__(cls)
    #     return cls._instance

    def __init__(self, session: aiohttp.ClientSession, fs: "Firestore"):
        self.session: aiohttp.ClientSession = session
        self.fs: "Firestore" = fs

    async def receive_token(
            self, sender_id: str | None = None, login: str | None = None,
            password: str | None = None
    ) -> str:
        """
        Receive auth token from s.letovo.ru

        Notes:
            Requires either a sender_id or (password and login)

        Args:
            sender_id (str | None): user's Telegram ID
            login (str | None): user's login to s.letovo.ru
            password (str | None): user's password to s.letovo.ru

        Raises:
            aiohttp.ClientConnectionError: if connection cannot be established to s.letovo.ru
            UnauthorizedError: if any other error caught during connection to s.letovo.ru
            NothingFoundError: if credentials cannot be found in the provided DB

        Returns:
            str: auth token
        """
        if None in {login, password}:
            login, password = await self.fs.get_data(
                sender_id=sender_id, values=[types_l.FSData.login, types_l.FSData.password]
            )
            if errors_l.NothingFoundError in {login, password}:
                raise errors_l.NothingFoundError(
                    creds_not_found_text
                )
        login_data = {
            "login": login,
            "password": password
        }
        try:
            async with self.session.post(url=settings().URL_LOGIN_LETOVO, data=login_data) as resp:
                if resp.status == 429:
                    log.error("Cannot get data from s.letovo.ru (too many requests). Error %d", resp.status)
                    raise errors_l.TooManyRequests()

                if resp.status != 200:
                    log.error("Cannot get data from s.letovo.ru. Error %d", resp.status)
                    raise errors_l.UnauthorizedError(f"Cannot get data from s.letovo.ru. Error {resp.status}")

                resp_j = await resp.json(loads=orjson.loads)
                return f'{resp_j["data"]["token_type"]} {resp_j["data"]["token"]}'
        except aiohttp.ClientConnectionError as err:
            log.exception(err)
            raise aiohttp.ClientConnectionError(no_conn_text)
        except asyncio.TimeoutError as err:
            log.exception(err)
            raise asyncio.TimeoutError(too_long_conn_text)

    async def receive_student_id(
            self, sender_id: str | None = None, token: str | None = None
    ) -> int:
        """
        Receive student id from s.letovo.ru

        Notes:
            Requires either a sender_id or token

        Args:
            sender_id (str | None): user's Telegram ID
            token (str | None): auth token to s.letovo.ru

        Raises:
            aiohttp.ClientConnectionError: if connection cannot be established to s.letovo.ru
            UnauthorizedError: if any other error caught during connection to s.letovo.ru
            NothingFoundError: if credentials cannot be found in the provided DB

        Returns:
            int: student id
        """
        if token is None:
            token = await self.fs.get_data(sender_id=sender_id, values=[types_l.FSData.token])
            if token is errors_l.NothingFoundError:
                raise errors_l.NothingFoundError(
                    creds_not_found_text
                )
        headers = {
            "Authorization": token
        }
        try:
            async with self.session.post(url="https://s-api.letovo.ru/api/me", headers=headers) as resp:
                if resp.status != 200:
                    log.error("Cannot get data from s.letovo.ru. Error %d", resp.status)
                    raise errors_l.UnauthorizedError(f"Cannot get data from s.letovo.ru. Error {resp.status}")
                resp_j = await resp.json(loads=orjson.loads)
                return int(resp_j["data"]["user"]["student_id"])
        except aiohttp.ClientConnectionError as err:
            log.exception(err)
            raise aiohttp.ClientConnectionError(no_conn_text)
        except asyncio.TimeoutError as err:
            log.exception(err)
            raise asyncio.TimeoutError(too_long_conn_text)

    async def receive_schedule_ics(
            self, sender_id: str
    ) -> bytes:
        """
        Receive schedule in ics from s.letovo.ru

        Args:
            sender_id (str): user's Telegram ID

        Raises:
            aiohttp.ClientConnectionError: if connection cannot be established to s.letovo.ru
            UnauthorizedError: if any other error caught during connection to s.letovo.ru
            NothingFoundError: if credentials cannot be found in the provided DB

        Returns:
            bytes
        """
        student_id, token = await self.fs.get_data(
            sender_id=sender_id, values=[types_l.FSData.student_id, types_l.FSData.token]
        )

        if errors_l.NothingFoundError in {student_id, token}:
            raise errors_l.NothingFoundError(
                creds_not_found_text
            )

        if int(datetime.datetime.now(tz=settings().timezone).strftime("%w")) == 0:
            date = (datetime.datetime.now(tz=settings().timezone) + datetime.timedelta(1))
        else:
            date = datetime.datetime.now(tz=settings().timezone)

        url = f"https://s-api.letovo.ru/api/schedule/{student_id}/week/ics?schedule_date={date:%Y-%m-%d}"

        headers = {
            "Authorization": token,
        }
        try:
            async with self.session.get(url=url, headers=headers, timeout=60) as resp:
                if resp.status != 200:
                    log.error("Cannot get data from s.letovo.ru. Error %d", resp.status)
                    raise errors_l.UnauthorizedError(f"Cannot get data from s.letovo.ru. Error {resp.status}")
                return await resp.read()
        except aiohttp.ClientConnectionError as err:
            log.exception(err)
            raise aiohttp.ClientConnectionError(no_conn_text)
        except asyncio.TimeoutError as err:
            log.exception(err)
            raise asyncio.TimeoutError(too_long_conn_text)

    async def receive_schedule_and_hw(
            self, sender_id: str, specific_day: types_l.Weekdays = None, *, week: bool = True
    ) -> dict:
        """
        Receive homework & schedule from s.letovo.ru

        Args:
            specific_day (types_l.Weekdays, optional):
            sender_id (str): user's Telegram ID
            week (bool, optional): receive schedule & hw for week or for current day

        Raises:
            aiohttp.ClientConnectionError: if connection cannot be established to s.letovo.ru
            UnauthorizedError: if any other error caught during connection to s.letovo.ru
            NothingFoundError: if credentials cannot be found in the provided DB

        Returns:
            json
        """
        student_id, token = await self.fs.get_data(
            sender_id=sender_id, values=[types_l.FSData.student_id, types_l.FSData.token]
        )

        if errors_l.NothingFoundError in {student_id, token}:
            raise errors_l.NothingFoundError(
                creds_not_found_text
            )

        if int(datetime.datetime.now(tz=settings().timezone).strftime("%w")) == 0:
            date = (datetime.datetime.now(tz=settings().timezone) + datetime.timedelta(1))
        else:
            date = datetime.datetime.now(tz=settings().timezone)

        if week:
            url = f"https://s-api.letovo.ru/api/schedule/{student_id}/week?schedule_date={date.strftime('%Y-%m-%d')}"
        else:
            delta = specific_day.value - int(date.strftime("%w"))
            date += datetime.timedelta(delta)
            url = f"https://s-api.letovo.ru/api/schedule/{student_id}/day?schedule_date={date.strftime('%Y-%m-%d')}"

        headers = {
            "Authorization": token,
        }
        try:
            async with self.session.get(url=url, headers=headers, timeout=60) as resp:
                if resp.status != 200:
                    log.error("Cannot get data from s.letovo.ru. Error %d", resp.status)
                    raise errors_l.UnauthorizedError(f"Cannot get data from s.letovo.ru. Error {resp.status}")
                return await resp.json(loads=orjson.loads)
        except aiohttp.ClientConnectionError as err:
            log.exception(err)
            raise aiohttp.ClientConnectionError(no_conn_text)
        except asyncio.TimeoutError as err:
            log.exception(err)
            raise asyncio.TimeoutError(too_long_conn_text)

    async def receive_marks_and_teachers(
            self, sender_id: str
    ) -> dict:
        """
        Receive marks & teachers' names from s.letovo.ru

        Args:
            sender_id (str): user's Telegram ID

        Raises:
            aiohttp.ClientConnectionError: if connection cannot be established to s.letovo.ru
            UnauthorizedError: if any other error caught during connection to s.letovo.ru
            NothingFoundError: if credentials cannot be found in the provided DB

        Returns:
            json
        """
        student_id, token = await self.fs.get_data(
            sender_id=sender_id, values=[types_l.FSData.student_id, types_l.FSData.token]
        )

        if errors_l.NothingFoundError in {student_id, token}:
            raise errors_l.NothingFoundError(
                creds_not_found_text
            )
        if int(datetime.datetime.now(tz=settings().timezone).strftime("%m")) >= 9:
            period_num = "1"
        else:
            period_num = "2"

        url = f"https://s-api.letovo.ru/api/schoolprogress/{student_id}?period_num={period_num}"

        headers = {
            "Authorization": token,
        }
        try:
            async with self.session.get(url=url, headers=headers, timeout=60) as resp:
                if resp.status != 200:
                    log.error("Cannot get data from s.letovo.ru. Error %d", resp.status)
                    raise errors_l.UnauthorizedError(f"Cannot get data from s.letovo.ru. Error {resp.status}")
                return await resp.json(loads=orjson.loads)
        except aiohttp.ClientConnectionError as err:
            log.exception(err)
            raise aiohttp.ClientConnectionError(no_conn_text)
        except asyncio.TimeoutError as err:
            log.exception(err)
            raise asyncio.TimeoutError(too_long_conn_text)
