from __future__ import annotations

import asyncio
import contextlib
import logging as log
import types
import typing

import aiohttp
import firebase_admin
import yaml
from firebase_admin import auth
from firebase_admin import credentials, _DEFAULT_APP_NAME
from google.cloud.firestore_v1.async_client import AsyncClient, AsyncDocumentReference, DocumentSnapshot
from google.cloud.firestore_v1.field_path import get_nested_value

from app.dependencies import errors as errors_l, types as types_l
from config import settings


@typing.final
class Firestore:
    """
    Class for dealing with Google Firestore database

    Args:
        app_name (str): name of the connection. If not specified, the default value will be used
    """
    __slots__ = ("_client", "app_name", "__counter")

    def __init__(self, app_name: str = _DEFAULT_APP_NAME):
        self._client: AsyncClient = ...
        self.app_name = app_name
        self._counter = 0

    async def __aenter__(self) -> Firestore:
        self._client = await self._connect()
        return self

    async def __aexit__(
            self,
            exc_type: type[BaseException] | None,
            exc_val: BaseException | None,
            exc_tb: types.TracebackType | None,
    ):
        self._client.close()

    @property
    def _counter(self) -> int:
        return self.__counter

    @_counter.setter
    def _counter(self, value: int):
        self.__counter = value

    @_counter.deleter
    def _counter(self):
        self.__counter = 0

    @classmethod
    async def create(cls, *, app_name: str = _DEFAULT_APP_NAME) -> Firestore:
        """
        Factory used for initializing database connection object

        Notes:
            Instead, use context manager, i.e. the `with` statement,
            because it allows you to forget about closing connections, etc.

        Args:
            app_name (str): name of the connection. If not provided, default will be used

        Returns:
            class instance with database connection
        """
        self = cls(app_name=app_name)
        self._client = await self._connect()
        return self

    async def _connect(self) -> AsyncClient:
        """
        Internal method used for connecting to the database

        Returns:
            database connection
        """
        app = firebase_admin.initialize_app(
            credential=credentials.Certificate(yaml.full_load(settings().GOOGLE_FS_KEY)), name=self.app_name
        )
        return AsyncClient(credentials=app.credential.get_credential(), project=app.project_id)

    async def disconnect(self):
        """
        Close the database connection

        Notes:
            Instead, use context manager, i.e. the `with` statement,
            because it allows you to forget about closing connections, etc.
        """
        self._client.close()

    async def send_email_to(self, analytics_login: str, /):
        with contextlib.suppress(auth.EmailAlreadyExistsError):
            auth.create_user(email=f"{analytics_login}@student.letovo.ru")
        await self._send_email_unsafe(email=f"{analytics_login}@student.letovo.ru")

    async def update_tokens(self, api: "API"):
        async for user in await self.get_users():
            try:
                token = await self._do_receive_token(api, user.id)
            except (errors_l.NothingFoundError, errors_l.UnauthorizedError, aiohttp.ClientConnectionError) as err:
                log.info(f"Skipped {user.id} {err}")
                continue

            await self.update_data(sender_id=user.id, token=token)
            log.info(f"Updated {user.id}")

        del self._counter

    async def _do_receive_token(self, api: "API", user_id: str) -> str:
        try:
            token = await api.receive_token(sender_id=user_id)
        except errors_l.TooManyRequests:
            await asyncio.sleep(25)

            if self._counter > 2:
                self._counter = 0
                raise aiohttp.ClientConnectionError()

            self._counter += 1
            token = await self._do_receive_token(api, user_id)

        return token

    @staticmethod
    async def _send_email_unsafe(email: str) -> bytes:
        """
        Email a new user informing them that registration succeeded

        Args:
            email (str): whom to send an email

        Returns:
            binary response
        """
        api_url: str = (
            "https://www.googleapis.com/identitytoolkit/v3/relyingparty/getOobConfirmationCode?key="
            f"{settings().GOOGLE_API_KEY}"
        )
        headers: dict = {
            "content-type": "application/json; charset=UTF-8"
        }
        data = f'{{"requestType": "PASSWORD_RESET", "email": "{email}"}}'

        async with aiohttp.ClientSession() as session:
            async with session.post(url=api_url, headers=headers, data=data) as resp:
                return await resp.content.read()

    async def update_data(
            self,
            sender_id: str,
            student_id: int | None = None,
            mail_address: str | None = None,
            mail_password: str | None = None,
            analytics_login: str | None = None,
            analytics_password: str | None = None,
            token: str | None = None,
            lang: str | None = None
    ):
        """
        Update user's data in the database

        Warnings:
            Fill in at least one param in each hashmap!
            Otherwise, all data will be erased there
        """
        space = ""
        st = f'"student_id": {student_id!r},'
        ma = f'"mail_address": {mail_address!r},'
        mp = f'"mail_password": {mail_password!r},'
        al = f'"analytics_login": {analytics_login!r},'
        ap = f'"analytics_password": {analytics_password!r},'
        t = f'"token": {token!r},'
        ll = f'"lang": {lang!r},'

        request_payload = (
            '''
        {
            "data": {'''
            f'{st if student_id else space}'
            f'{ma if mail_address else space}'
            f'{mp if mail_password else space}'
            f'{al if analytics_login else space}'
            f'{ap if analytics_password else space}'
            f'{t if token else space}'
            '".service": "data"'
            '''},
                "preferences": {'''
            f'{ll if lang else space}'
            '".service": "preferences"'
            '''}
        }'''
        )
        doc_ref: AsyncDocumentReference = self._client.collection("users").document(sender_id)
        await doc_ref.set(yaml.full_load(request_payload), merge=True)

    async def update_name(
            self,
            sender_id: str,
            first_name: int | None = None,
            last_name: str | None = None,
    ):
        """
        Update user's name in the database

        Warnings:
            Fill in at least one param in each hashmap!
            Otherwise, all data will be erased there
        """
        space = ""
        fn = f'"first_name": {first_name!r},'
        la = f'"last_name": {last_name!r},'

        request_payload = (
            '''
        {
            "data": {'''
            f'{fn if first_name else space}'
            f'{la if last_name else space}'
            '".service": "data"'
            '''}
        }'''
        )
        doc_ref: AsyncDocumentReference = self._client.collection("names").document(sender_id)
        await doc_ref.set(yaml.full_load(request_payload), merge=True)

    async def is_logged(self, sender_id: str) -> bool:
        """
        Check the user's presence in the database.

        Args:
            sender_id (str): user's Telegram ID

        Returns:
            bool: `True` if user's credentials are present in the database. Otherwise, `False`
        """
        doc: DocumentSnapshot = await self._client.collection("users").document(sender_id).get()
        try:
            return bool(doc.get("data.analytics_password"))
        except KeyError:
            return False

    async def get_users(self) -> typing.AsyncIterator[DocumentSnapshot]:
        """
        Get users' IDs to easily iterate over

        Returns:
            AsyncIterator
        """
        return self._client.collection("users").stream()

    async def get_data(self, sender_id: str, values: list[types_l.FSData]):
        """
        Get user's data from the database

        Args:
            sender_id (str): user's Telegram ID
            values (list of types_l.FSData):

        Returns:
            list of (asked value or `errors_l.NothingFoundError` if not found in the database)
        """
        resp = []
        doc = (await self._client.collection("users").document(sender_id).get()).to_dict()
        for value in values:
            try:
                resp.append(get_nested_value(str(value.value), doc))
            except KeyError:
                resp.append(errors_l.NothingFoundError)

        return resp

    async def get_name(self, sender_id: str, values: list[types_l.FSNames]):
        """
        Get user's data from the database

        Args:
            sender_id (str): user's Telegram ID
            values (list of types_l.FSNames):

        Returns:
            list of (asked value or `errors_l.NothingFoundError` if not found in the database)
        """
        resp = []
        doc = (await self._client.collection("names").document(sender_id).get()).to_dict()
        for value in values:
            try:
                resp.append(get_nested_value(str(value.value), doc))
            except KeyError:
                resp.append(errors_l.NothingFoundError)

        return resp
