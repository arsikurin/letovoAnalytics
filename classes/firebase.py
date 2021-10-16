#!/usr/bin/python3.10

import yaml
import firebase_admin
import requests as rq

from typing import Type
from firebase_admin import credentials
from google.cloud.firestore_v1.async_client import AsyncClient, AsyncDocumentReference, DocumentSnapshot
from constants import GOOGLE_KEY, API_KEY
from classes.errors import NothingFoundError

app = firebase_admin.initialize_app(
    credentials.Certificate(yaml.full_load(GOOGLE_KEY)))
firestore = AsyncClient(credentials=app.credential.get_credential(), project=app.project_id)


class FirebaseSetters:
    @staticmethod
    async def update_data(
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
        doc_ref: AsyncDocumentReference = firestore.collection(u"users").document(sender_id)
        await doc_ref.set(yaml.full_load(request_payload), merge=True)

    @staticmethod
    async def update_name(
            sender_id: str,
            first_name: int | None = None,
            last_name: str | None = None,
    ):
        """
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
        doc_ref: AsyncDocumentReference = firestore.collection(u"names").document(sender_id)
        await doc_ref.set(yaml.full_load(request_payload), merge=True)


class FirebaseGetters:
    @staticmethod
    async def is_inited(sender_id: str) -> bool:
        docs = firestore.collection(u"users").stream()
        return sender_id in [doc.id async for doc in docs]

    @staticmethod
    async def get_users() -> list:
        docs = firestore.collection(u"users").stream()
        return [doc.id async for doc in docs]

    @staticmethod
    async def get_student_id(sender_id: str) -> int | Type[NothingFoundError]:
        doc: DocumentSnapshot = await firestore.collection(u"users").document(sender_id).get()
        try:
            if not doc.exists:
                return NothingFoundError
            return doc.get("data.student_id")
        except KeyError:
            return NothingFoundError

    @staticmethod
    async def get_token(sender_id: str) -> str | Type[NothingFoundError]:
        doc: DocumentSnapshot = await firestore.collection(u"users").document(sender_id).get()
        try:
            if not doc.exists:
                return NothingFoundError
            return doc.get("data.token")
        except KeyError:
            return NothingFoundError

    @staticmethod
    async def get_password(sender_id: str) -> str | Type[NothingFoundError]:
        doc: DocumentSnapshot = await firestore.collection(u"users").document(sender_id).get()
        try:
            if not doc.exists:
                return NothingFoundError
            return doc.get("data.analytics_password")
        except KeyError:
            return NothingFoundError

    @staticmethod
    async def get_login(sender_id: str) -> str | Type[NothingFoundError]:
        doc: DocumentSnapshot = await firestore.collection(u"users").document(sender_id).get()
        try:
            if not doc.exists:
                return NothingFoundError
            return doc.get("data.analytics_login")
        except KeyError:
            return NothingFoundError

    @staticmethod
    async def get_name(sender_id: str) -> str | Type[NothingFoundError]:
        doc: DocumentSnapshot = await firestore.collection(u"names").document(sender_id).get()
        try:
            if not doc.exists:
                return NothingFoundError
            return doc.get("data.first_name")
        except KeyError:
            return NothingFoundError


class Firebase(FirebaseGetters, FirebaseSetters):
    """
    Class for working with Google Firebase
    """

    @staticmethod
    async def send_email(email):
        api_url = f"https://www.googleapis.com/identitytoolkit/v3/relyingparty/getOobConfirmationCode?key={API_KEY}"
        headers = {
            "content-type": "application/json; charset=UTF-8"
        }
        data = f'{{"requestType": "PASSWORD_RESET", "email": "{email}"}}'
        request_object = rq.post(api_url, headers=headers, data=data)
        return request_object.json()
