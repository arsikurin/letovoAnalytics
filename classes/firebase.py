#!/usr/bin/python3.10

import yaml
import firebase_admin

from typing import Type
from firebase_admin import credentials
from google.cloud.firestore_v1.async_client import AsyncClient, AsyncDocumentReference, DocumentSnapshot
from constants import GOOGLE_KEY
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

    @staticmethod
    async def update_analytics(
            sender_id: str,
            schedule_entire: int | None = None,
            schedule_today: int | None = None,
            schedule_specific: int | None = None,
            homework_entire: int | None = None,
            homework_tomorrow: int | None = None,
            homework_specific: int | None = None,
            marks_all: int | None = None,
            marks_summative: int | None = None,
            marks_recent: int | None = None,
            holidays: int | None = None,
            clear_previous: int | None = None,
            options: int | None = None,
            help: int | None = None,
            start: int | None = None,
            about: int | None = None,
            inline: int | None = None
    ):
        """
        Fill in at least one param in each map!
        Otherwise, all data will be erased there
        """
        doc_ref: AsyncDocumentReference = firestore.collection(u"analytics").document(sender_id)
        if schedule_entire:
            schedule_entire += int((await doc_ref.get()).get("data.schedule_entire"))
        if schedule_today:
            schedule_today += int((await doc_ref.get()).get("data.schedule_today"))
        if schedule_specific:
            schedule_specific += int((await doc_ref.get()).get("data.schedule_specific"))
        if homework_entire:
            homework_entire += int((await doc_ref.get()).get("data.homework_entire"))
        if homework_tomorrow:
            homework_tomorrow += int((await doc_ref.get()).get("data.homework_tomorrow"))
        if homework_specific:
            homework_specific += int((await doc_ref.get()).get("data.homework_specific"))
        if marks_all:
            marks_all += int((await doc_ref.get()).get("data.marks_all"))
        if marks_summative:
            marks_summative += int((await doc_ref.get()).get("data.marks_summative"))
        if marks_recent:
            marks_recent += int((await doc_ref.get()).get("data.marks_recent"))
        if holidays:
            holidays += int((await doc_ref.get()).get("data.holidays"))
        if clear_previous:
            clear_previous += int((await doc_ref.get()).get("data.clear_previous"))
        if options:
            options += int((await doc_ref.get()).get("data.options"))
        if help:
            help += int((await doc_ref.get()).get("data.help"))
        if start:
            start += int((await doc_ref.get()).get("data.start"))
        if about:
            about += int((await doc_ref.get()).get("data.about"))
        if inline:
            inline += int((await doc_ref.get()).get("data.inline"))

        space = ""
        se = f'"schedule_entire": {schedule_entire!r},'
        st = f'"schedule_today": {schedule_today!r},'
        ss = f'"schedule_specific": {schedule_specific!r},'
        he = f'"homework_entire": {homework_entire!r},'
        ht = f'"homework_tomorrow": {homework_tomorrow!r},'
        hs = f'"homework_specific": {homework_specific!r},'
        ma = f'"marks_all": {marks_all!r},'
        ms = f'"marks_summative": {marks_summative!r},'
        mr = f'"marks_recent": {marks_recent!r},'
        ho = f'"holidays": {holidays!r},'
        cp = f'"clear_previous": {clear_previous!r},'
        o = f'"options": {options!r},'
        h = f'"help": {help!r},'
        s = f'"start": {start!r},'
        a = f'"about": {about!r},'
        i = f'"inline": {inline!r},'

        request_payload = (
            '''
        {
            "data": {'''
            f'{se if schedule_entire is not None else space}'
            f'{st if schedule_today is not None else space}'
            f'{ss if schedule_specific is not None else space}'
            f'{he if homework_entire is not None else space}'
            f'{ht if homework_tomorrow is not None else space}'
            f'{hs if homework_specific is not None else space}'
            f'{ma if marks_all is not None else space}'
            f'{ms if marks_summative is not None else space}'
            f'{mr if marks_recent is not None else space}'
            f'{ho if holidays is not None else space}'
            f'{cp if clear_previous is not None else space}'
            f'{o if options is not None else space}'
            f'{h if help is not None else space}'
            f'{s if start is not None else space}'
            f'{a if about is not None else space}'
            f'{i if inline is not None else space}'
            '".service": "data"'
            '''}
        }'''
        )
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
    async def get_analytics_password(sender_id: str) -> str | Type[NothingFoundError]:
        doc: DocumentSnapshot = await firestore.collection(u"users").document(sender_id).get()
        try:
            if not doc.exists:
                return NothingFoundError
            return doc.get("data.analytics_password")
        except KeyError:
            return NothingFoundError

    @staticmethod
    async def get_analytics_login(sender_id: str) -> str | Type[NothingFoundError]:
        doc: DocumentSnapshot = await firestore.collection(u"users").document(sender_id).get()
        try:
            if not doc.exists:
                return NothingFoundError
            return doc.get("data.analytics_login")
        except KeyError:
            return NothingFoundError


class Firebase(FirebaseGetters, FirebaseSetters):
    """
    Class for working with Firestore DB
    """
