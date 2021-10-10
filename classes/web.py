#!/usr/bin/python3.10

import requests as rq
import asyncio
import datetime

from typing import Type
from concurrent.futures import Future, as_completed
from requests_futures.sessions import FuturesSession
from classes.errors import NothingFoundError, UnauthorizedError
from classes.firebase import Firebase
from constants import LOGIN_URL_LETOVO


class Web:
    """
    Class for working with web requests
    """

    @staticmethod
    async def receive_token(
            s: FuturesSession, sender_id: str | None = None, login: str | None = None, password: str | None = None
    ) -> str | Type[rq.ConnectionError] | Type[UnauthorizedError]:
        """
        Requires either a sender_id or (password and login)
        """
        if None in (login, password):
            login, password = await asyncio.gather(
                Firebase.get_analytics_login(sender_id=sender_id),
                Firebase.get_analytics_password(sender_id=sender_id)
            )
            if NothingFoundError in (login, password):
                return UnauthorizedError

        login_data = {
            "login": login,
            "password": password
        }
        try:
            login_future: Future = s.post(url=LOGIN_URL_LETOVO, data=login_data)
            for login_futured in as_completed((login_future,)):
                login_response = login_futured.result()
                return f'{login_response.json()["data"]["token_type"]} {login_response.json()["data"]["token"]}'
        except rq.ConnectionError:
            return rq.ConnectionError

    @staticmethod
    async def receive_student_id(
            s: FuturesSession, sender_id: str = None, token: str = None
    ) -> int | Type[rq.ConnectionError] | Type[UnauthorizedError]:
        """
        Requires either a sender_id or token
        """
        if token is None:
            token = await Firebase.get_token(sender_id=sender_id)
            if token == NothingFoundError:
                return UnauthorizedError

        me_headers = {
            "Authorization": token
        }
        try:
            me_future: Future = s.post("https://s-api.letovo.ru/api/me", headers=me_headers)
            for me_futured in as_completed((me_future,)):
                return int(me_futured.result().json()["data"]["user"]["student_id"])
        except rq.ConnectionError:
            return rq.ConnectionError

    @staticmethod
    async def receive_hw_n_schedule(
            s: FuturesSession, sender_id: str
    ) -> Future | Type[rq.ConnectionError] | Type[UnauthorizedError]:
        student_id, token = await asyncio.gather(
            Firebase.get_student_id(sender_id=sender_id),
            Firebase.get_token(sender_id=sender_id)
        )
        if NothingFoundError in (student_id, token):
            return UnauthorizedError

        homework_url = (
            f"https://s-api.letovo.ru/api/schedule/{student_id}/week?schedule_date="
            f"{datetime.datetime.now().date()}"
        )
        homework_headers = {
            "Authorization": token,
        }
        try:
            homework_future: Future = s.get(url=homework_url, headers=homework_headers)
            if homework_future.result().status_code != 200:
                return UnauthorizedError
        except rq.ConnectionError:
            return rq.ConnectionError
        return homework_future

    @staticmethod
    async def receive_marks(
            s: FuturesSession, sender_id: str
    ) -> Future | Type[rq.ConnectionError] | Type[UnauthorizedError]:
        student_id, token = await asyncio.gather(
            Firebase.get_student_id(sender_id=sender_id),
            Firebase.get_token(sender_id=sender_id)
        )
        if NothingFoundError in (student_id, token):
            return UnauthorizedError
        # TODO period_num
        marks_url = f"https://s-api.letovo.ru/api/schoolprogress/{student_id}?period_num=1"
        marks_headers = {
            "Authorization": token,
        }
        try:
            marks_future: Future = s.get(url=marks_url, headers=marks_headers)
            if marks_future.result().status_code != 200:
                return UnauthorizedError
        except rq.ConnectionError:
            return rq.ConnectionError
        return marks_future
