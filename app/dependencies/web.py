import asyncio
import time
import logging as log
import typing

import aiohttp
import orjson

from app.dependencies import errors as errors_l, CredentialsDatabase
from config import settings


@typing.final
class Web:
    """
    Class for dealing with web API of s.letovo.ru
    """
    __slots__ = ("_session",)

    def __init__(self, session: aiohttp.ClientSession):
        self.session: aiohttp.ClientSession = session

    @property
    def session(self) -> aiohttp.ClientSession:
        return self._session

    @session.setter
    def session(self, value: aiohttp.ClientSession):
        self._session = value

    async def receive_token(
            self, fs: CredentialsDatabase, sender_id: str | None = None, login: str | None = None,
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
                fs.get_login(sender_id=sender_id),
                fs.get_password(sender_id=sender_id)
            )
            if errors_l.NothingFoundError in (login, password):
                raise errors_l.NothingFoundError("Nothing found in the database for this user")

        login_data = {
            "login": login,
            "password": password
        }
        try:
            async with self.session.post(url=settings().URL_LOGIN_LETOVO, data=login_data) as resp:
                if resp.status != 200:
                    raise errors_l.UnauthorizedError(f"Cannot get data from s.letovo.ru. Error {resp.status}")
                resp_j = await resp.json(loads=orjson.loads)
                return f'{resp_j["data"]["token_type"]} {resp_j["data"]["token"]}'
        except aiohttp.ClientConnectionError:
            raise aiohttp.ClientConnectionError("Cannot establish connection to s.letovo.ru")

    async def receive_student_id(
            self, fs: CredentialsDatabase, sender_id: str = None, token: str = None
    ) -> int:
        """
        Requires either a sender_id or token

        :raise aiohttp.ClientConnectionError:
        :raise UnauthorizedError:
        :raise NothingFoundError:

        :return: int
        """
        if token is None:
            token = await fs.get_token(sender_id=sender_id)
            if token is errors_l.NothingFoundError:
                raise errors_l.NothingFoundError("Nothing found in the database for this user")

        headers = {
            "Authorization": token
        }
        try:
            async with self.session.post(url="https://s-api.letovo.ru/api/me", headers=headers) as resp:
                if resp.status != 200:
                    raise errors_l.UnauthorizedError(f"Cannot get data from s.letovo.ru. Error {resp.status}")
                resp_j = await resp.json(loads=orjson.loads)
                return int(resp_j["data"]["user"]["student_id"])
        except aiohttp.ClientConnectionError:
            raise aiohttp.ClientConnectionError("Cannot establish connection to s.letovo.ru")

    async def receive_hw_n_schedule(
            self, sender_id: str, fs: CredentialsDatabase
    ) -> bytes:
        """
        Receive homework & schedule

        :raise aiohttp.ClientConnectionError:
        :raise UnauthorizedError:
        :raise NothingFoundError:

        :return: bytes
        """
        student_id, token = await asyncio.gather(
            fs.get_student_id(sender_id=sender_id),
            fs.get_token(sender_id=sender_id)
        )
        if errors_l.NothingFoundError in (student_id, token):
            raise errors_l.NothingFoundError("Nothing found in the database for this user")

        url = (
            f"https://s-api.letovo.ru/api/schedule/{student_id}/week?schedule_date="
            f"{time.strftime('%Y-%m-%d')}"
        )
        headers = {
            "Authorization": token,
        }

        try:
            async with self.session.get(url=url, headers=headers) as resp:
                if resp.status != 200:
                    raise errors_l.UnauthorizedError(f"Cannot get data from s.letovo.ru. Error {resp.status}")
                return await resp.content.read()
        except aiohttp.ClientConnectionError as err:
            log.error(err)
            raise aiohttp.ClientConnectionError("Cannot establish connection to s.letovo.ru")

    async def receive_marks(
            self, sender_id: str, fs: CredentialsDatabase
    ) -> bytes:
        """
        Receive marks

        :raise aiohttp.ClientConnectionError:
        :raise UnauthorizedError:
        :raise NothingFoundError:

        :return: bytes
        """
        student_id, token = await asyncio.gather(
            fs.get_student_id(sender_id=sender_id),
            fs.get_token(sender_id=sender_id)
        )
        if errors_l.NothingFoundError in (student_id, token):
            raise errors_l.NothingFoundError("Nothing found in the database for this user")

        url = f"https://s-api.letovo.ru/api/schoolprogress/{student_id}?period_num="
        if int(time.strftime("%m")) >= 9:
            url += "1"
        else:
            url += "2"

        headers = {
            "Authorization": token,
        }

        try:
            async with self.session.get(url=url, headers=headers) as resp:
                if resp.status != 200:
                    raise errors_l.UnauthorizedError(f"Cannot get data from s.letovo.ru. Error {resp.status}")
                return await resp.content.read()
        except aiohttp.ClientConnectionError as err:
            log.error(err)
            raise aiohttp.ClientConnectionError("Cannot establish connection to s.letovo.ru")
