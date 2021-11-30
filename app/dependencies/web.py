import asyncio
import datetime
import logging as log
import typing

import aiohttp
import orjson

from app.dependencies import NothingFoundError, UnauthorizedError, Firebase
from config import settings


@typing.final
class Web:
    """
    Class for working with web API of s.letovo.ru
    """
    __slots__ = ("_session",)

    def __init__(self, session):
        self.session: aiohttp.ClientSession = session

    @property
    def session(self):
        return self._session

    @session.setter
    def session(self, value):
        self._session = value

    async def receive_token(
            self, sender_id: str | None = None, login: str | None = None,
            password: str | None = None
    ) -> str:
        """
        Requires either a sender_id or (password and login)

        :raise aiohttp.ClientConnectionError:
        :raise UnauthorizedError:
        :raise NothingFoundError:

        :return: str
        """
        if None in (login, password):
            login, password = await asyncio.gather(
                Firebase.get_login(sender_id=sender_id),
                Firebase.get_password(sender_id=sender_id)
            )
            if NothingFoundError in (login, password):
                raise NothingFoundError("Nothing found in the database for this user")

        login_data = {
            "login": login,
            "password": password
        }
        try:
            async with self.session.post(url=settings().URL_LOGIN_LETOVO, data=login_data) as resp:
                if resp.status != 200:
                    raise UnauthorizedError(f"Cannot get data from s.letovo.ru. Error {resp.status}")
                resp_j = await resp.json(loads=orjson.loads)
                return f'{resp_j["data"]["token_type"]} {resp_j["data"]["token"]}'
        except aiohttp.ClientConnectionError:
            raise aiohttp.ClientConnectionError("Cannot establish connection to s.letovo.ru")

    async def receive_student_id(
            self, sender_id: str = None, token: str = None
    ) -> int:
        """
        Requires either a sender_id or token

        :raise aiohttp.ClientConnectionError:
        :raise UnauthorizedError:
        :raise NothingFoundError:

        :return: int
        """
        if token is None:
            token = await Firebase.get_token(sender_id=sender_id)
            if token is NothingFoundError:
                raise NothingFoundError("Nothing found in the database for this user")

        headers = {
            "Authorization": token
        }
        try:
            async with self.session.post(url="https://s-api.letovo.ru/api/me", headers=headers) as resp:
                if resp.status != 200:
                    raise UnauthorizedError(f"Cannot get data from s.letovo.ru. Error {resp.status}")

                resp_j = await resp.json(loads=orjson.loads)
                return int(resp_j["data"]["user"]["student_id"])
        except aiohttp.ClientConnectionError:
            raise aiohttp.ClientConnectionError("Cannot establish connection to s.letovo.ru")

    async def receive_hw_n_schedule(
            self, sender_id: str
    ) -> bytes:
        """
        Receive homework & schedule

        :raise aiohttp.ClientConnectionError:
        :raise UnauthorizedError:
        :raise NothingFoundError:

        :return: bytes
        """
        student_id, token = await asyncio.gather(
            Firebase.get_student_id(sender_id=sender_id),
            Firebase.get_token(sender_id=sender_id)
        )
        if NothingFoundError in (student_id, token):
            raise NothingFoundError("Nothing found in the database for this user")

        url = (
            f"https://s-api.letovo.ru/api/schedule/{student_id}/week?schedule_date="
            f"{datetime.datetime.now().date()}"
        )
        headers = {
            "Authorization": token,
        }

        try:
            async with self.session.get(url=url, headers=headers) as resp:
                if resp.status != 200:
                    raise UnauthorizedError(f"Cannot get data from s.letovo.ru. Error {resp.status}")
                return await resp.content.read()
                # return await resp.json()
        except aiohttp.ClientConnectionError as err:
            log.error(err)
            raise aiohttp.ClientConnectionError("Cannot establish connection to s.letovo.ru")

    async def receive_marks(
            self, sender_id: str
    ) -> bytes:
        """
        Receive marks

        :raise aiohttp.ClientConnectionError:
        :raise UnauthorizedError:
        :raise NothingFoundError:

        :return: bytes
        """
        student_id, token = await asyncio.gather(
            Firebase.get_student_id(sender_id=sender_id),
            Firebase.get_token(sender_id=sender_id)
        )
        if NothingFoundError in (student_id, token):
            raise NothingFoundError("Nothing found in the database for this user")

        # TODO period_num
        url = f"https://s-api.letovo.ru/api/schoolprogress/{student_id}?period_num=1"

        headers = {
            "Authorization": token,
        }

        try:
            async with self.session.get(url=url, headers=headers) as resp:
                if resp.status != 200:
                    raise UnauthorizedError(f"Cannot get data from s.letovo.ru. Error {resp.status}")
                # return await resp.json()
                return await resp.content.read()
        except aiohttp.ClientConnectionError as err:
            log.error(err)
            raise aiohttp.ClientConnectionError("Cannot establish connection to s.letovo.ru")
