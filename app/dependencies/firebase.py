from __future__ import annotations

import types
import typing

import aiohttp
import firebase_admin
import yaml
from firebase_admin import credentials, _DEFAULT_APP_NAME
from google.cloud.firestore_v1.async_client import AsyncClient, AsyncDocumentReference, DocumentSnapshot

from app.dependencies import errors as errors_l
from config import settings


@typing.final
class Firestore:
    """
    Class for dealing with Google Firestore database

    Args:
        app_name (str): name of the connection. If not provided, default will be used
    """
    __slots__ = ("__client", "_app_name")

    def __init__(self, app_name: str = _DEFAULT_APP_NAME):
        self._client: AsyncClient = ...
        self.app_name = app_name

    async def __aenter__(self) -> Firestore:
        self._client = await self._connect()
        return self

    async def __aexit__(
            self,
            exc_type: typing.Type[BaseException] | None,
            exc_val: BaseException | None,
            exc_tb: types.TracebackType | None,
    ):
        self._client.close()

    @property
    def _client(self) -> AsyncClient:
        return self.__client

    @_client.setter
    def _client(self, value: AsyncClient):
        self.__client = value

    @property
    def app_name(self) -> str:
        return self._app_name

    @app_name.setter
    def app_name(self, value: str):
        self._app_name = value

    @staticmethod
    async def create(*, app_name: str = _DEFAULT_APP_NAME) -> Firestore:
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
        self = Firestore()
        self.app_name = app_name
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

    @staticmethod
    async def send_email_to(email: str, /):
        """
        Email a new user informing them that registration succeeded

        Args:
            email (str): whom to send an email
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
            Fill in at least one param in each map!
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
            Fill in at least one param in each map!
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

    async def is_inited(self, sender_id: str) -> bool:
        """
        Check the user's presence in the database

        Notes:
            Instead, use `is_logged` because current method requires more time to execute
            and cannot verify the registration status

        Args:
            sender_id (str): user's Telegram ID

        Returns:
            bool
        """
        docs = self._client.collection("users").stream()
        return sender_id in [doc.id async for doc in docs]

    async def is_logged(self, sender_id: str) -> bool:
        """
        Check the user's presence in the database.

        Args:
            sender_id (str): user's Telegram ID

        Returns:
            bool: `True` if user's credentials are in presented in the database. Otherwise, `False`
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

    async def get_student_id(self, sender_id: str) -> int | typing.Type[errors_l.NothingFoundError]:
        """
        Get user's student ID

        Args:
            sender_id (str): user's Telegram ID

        Returns:
            student ID (int) or errors_l.NothingFoundError if not found in the database
        """
        doc: DocumentSnapshot = await self._client.collection("users").document(sender_id).get()
        try:
            if not doc.exists:
                return errors_l.NothingFoundError
            return doc.get("data.student_id")
        except KeyError:
            return errors_l.NothingFoundError

    async def get_token(self, sender_id: str) -> str | typing.Type[errors_l.NothingFoundError]:
        """
        Get user's auth token

        Args:
            sender_id (str): user's Telegram ID

        Returns:
            auth token (str) or errors_l.NothingFoundError if not found in the database
        """
        doc: DocumentSnapshot = await self._client.collection("users").document(sender_id).get()
        try:
            if not doc.exists:
                return errors_l.NothingFoundError
            return doc.get("data.token")
        except KeyError:
            return errors_l.NothingFoundError

    async def get_password(self, sender_id: str) -> str | typing.Type[errors_l.NothingFoundError]:
        """
        Get user's password

        Args:
            sender_id (str): user's Telegram ID

        Returns:
            password (str) or errors_l.NothingFoundError if not found in the database
        """
        doc: DocumentSnapshot = await self._client.collection("users").document(sender_id).get()
        try:
            if not doc.exists:
                return errors_l.NothingFoundError
            return doc.get("data.analytics_password")
        except KeyError:
            return errors_l.NothingFoundError

    async def get_login(self, sender_id: str) -> str | typing.Type[errors_l.NothingFoundError]:
        """
        Get user's login

        Args:
            sender_id (str): user's Telegram ID

        Returns:
            login (str) or errors_l.NothingFoundError if not found in the database
        """
        doc: DocumentSnapshot = await self._client.collection("users").document(sender_id).get()
        try:
            if not doc.exists:
                return errors_l.NothingFoundError
            return doc.get("data.analytics_login")
        except KeyError:
            return errors_l.NothingFoundError

    async def get_name(self, sender_id: str) -> str | typing.Type[errors_l.NothingFoundError]:
        """
        Get user's name

        Args:
            sender_id (str): user's Telegram ID

        Returns:
            name (str) or errors_l.NothingFoundError if not found in the database
        """
        doc: DocumentSnapshot = await self._client.collection("names").document(sender_id).get()
        try:
            if not doc.exists:
                return errors_l.NothingFoundError
            return doc.get("data.first_name")
        except KeyError:
            return errors_l.NothingFoundError

    async def get_surname(self, sender_id: str) -> str | typing.Type[errors_l.NothingFoundError]:
        """
        Get user's surname

        Args:
            sender_id (str): user's Telegram ID

        Returns:
            surname (int) or errors_l.NothingFoundError if not found in the database
        """
        doc: DocumentSnapshot = await self._client.collection("names").document(sender_id).get()
        try:
            if not doc.exists:
                return errors_l.NothingFoundError
            return doc.get("data.last_name")
        except KeyError:
            return errors_l.NothingFoundError
