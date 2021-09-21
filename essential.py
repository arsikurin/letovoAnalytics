#!/usr/bin/python3.9

import os
import yaml
import asyncio
import datetime
import firebase_admin
import requests as rq
import logging as log

# from debug import *
from enum import Enum  # , auto
from ics import Calendar
# from imaplib import IMAP4_SSL
# from bs4 import BeautifulSoup
from colourlib import Fg, Style
from typing import Optional, Any
# from email import message_from_string
from firebase_admin import firestore, credentials
from concurrent.futures import as_completed, Future
from requests_futures.sessions import FuturesSession
from telethon import Button, events, types
from google.cloud.firestore_v1.document import DocumentReference, DocumentSnapshot

#
# --------------------- Constants
LOGIN_URL_LETOVO = "https://s-api.letovo.ru/api/login"
MAIN_URL_LETOVO = "https://s.letovo.ru"
MAIN_URL_API = "https://letovo-analytics.herokuapp.com/"
LOGIN_URL_LOCAL = "https://letovo-analytics.web.app/login"
API_KEY = os.environ["API_KEY"]
API_ID = os.environ["API_ID"]
API_HASH = os.environ["API_HASH"]
BOT_TOKEN = os.environ["BOT_TOKEN"]
HOST_SQL = os.environ["HOST_SQL"]
PORT_SQL = "5432"
USER_SQL = os.environ["USER_SQL"]
DATABASE_SQL = os.environ["DATABASE_SQL"]
PASSWORD_SQL = os.environ["PASSWORD_SQL"]

#
# --------------------- Firestore
firebase_admin.initialize_app(
    credentials.Certificate(yaml.full_load(os.environ["GOOGLE_KEY"])))
firedb = firestore.client()

#
# --------------------- Parsing
# TODO scrapy(w/ or w/o BF), selenium, apis listed below
# soup = BeautifulSoup(html, "lxml")
# f"https://s-api.letovo.ru/api/students/{student_id}"
# f"https://s-api.letovo.ru/api/studentsimg/{student_id}"
# f"https://s-api.letovo.ru/api/schoolprogress/{student_id}/widget?period_num=1"
# f"https://s-api.letovo.ru/api/schoolprogress/{student_id}?period_num=1"
# f"https://s-api.letovo.ru/api/schedulelesson/477229/5876484/{student_id}?schedule_date={date}"
# f"https://s-api.letovo.ru/api/schedule/{student_id}/widget"
# SCHEDULE PLAN & HW f"https://s-api.letovo.ru/api/schedule/{student_id}/day?schedule_date={date}"
# f"https://s-api.letovo.ru/api/schedule/{student_id}/week/ics?schedule_date="

#
# --------------------- Debug
custom_DEBUG: bool = True
# start_time = time.perf_counter()
# datetime.timedelta(seconds=time.perf_counter() - start_time)

if custom_DEBUG:
    log.basicConfig(
        format=f"{Fg.Green}{Style.Bold}%(asctime)s{Fg.Reset}{Style.Bold} %(message)s{Style.Reset}\n[%(name)s]\n",
        level=log.DEBUG
    )
else:
    log.basicConfig(
        format=f"{Fg.Green}{Style.Bold}%(asctime)s{Fg.Reset}{Style.Bold} %(message)s{Style.Reset}\n[%(name)s]\n",
        level=log.DEBUG
    )
    log.getLogger("urllib3.connectionpool").disabled = True
    log.getLogger("asyncio").disabled = True
    log.getLogger("telethon.network.mtprotosender").disabled = True
    log.getLogger("telethon.extensions.messagepacker").disabled = True
    log.getLogger("telethon.client.uploads").disabled = True


# class CustomError(Exception):
#     """
#     Occurs when another exclusive conversation is opened in the same chat.
#     """
#
#     def __init__(self):
#         super().__init__(
#             "variable referenced before assignment"
#         )

class NothingFoundError(Exception):
    """
    Occurs when anything cannot by found in the database
    """

    def __init__(self):
        super().__init__(
            "The data you are looking for does not exist"
        )


class Weekdays(Enum):
    Monday = 1
    Tuesday = 2
    Wednesday = 3
    Thursday = 4
    Friday = 5
    Saturday = 6


class FirebaseSetters:
    @staticmethod
    async def update_data(
            sender_id: str,
            student_id: Optional[int] = None,
            mail_address: Optional[str] = None,
            mail_password: Optional[str] = None,
            analytics_login: Optional[str] = None,
            analytics_password: Optional[str] = None,
            token: Optional[str] = None,
            lang: Optional[str] = None
    ) -> None:
        """
        Fill out at least one param in every map!!!
        Otherwise all data in map will be erased
        """
        space: str = ""
        st: str = f'"student_id": {student_id!r},'
        ma: str = f'"mail_address": {mail_address!r},'
        mp: str = f'"mail_password": {mail_password!r},'
        al: str = f'"analytics_login": {analytics_login!r},'
        ap: str = f'"analytics_password": {analytics_password!r},'
        t: str = f'"token": {token!r},'
        ll: str = f'"lang": {lang!r},'

        request_payload: str = (
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
        doc_ref: DocumentReference = firedb.collection(u"users").document(sender_id)
        doc_ref.set(yaml.full_load(request_payload), merge=True)


class FirebaseGetters:
    @staticmethod
    async def is_inited(sender_id: str) -> bool:
        docs = firedb.collection(u"users").stream()
        if sender_id in [doc.id for doc in docs]:
            return True
        return False

    @staticmethod
    async def get_users() -> list:
        return [doc.id for doc in firedb.collection(u"users").stream()]

    @staticmethod
    async def get_student_id(sender_id: str):
        doc: DocumentSnapshot = firedb.collection(u"users").document(sender_id).get()
        try:
            if doc.exists:
                return doc.to_dict()["data"]["student_id"]
        except KeyError:
            return None

    @staticmethod
    async def get_token(sender_id: str):
        doc: DocumentSnapshot = firedb.collection(u"users").document(sender_id).get()
        try:
            if doc.exists:
                return doc.to_dict()["data"]["token"]
        except KeyError:
            return None

    @staticmethod
    async def get_analytics_password(sender_id: str):
        doc: DocumentSnapshot = firedb.collection(u"users").document(sender_id).get()
        try:
            if doc.exists:
                return doc.to_dict()["data"]["analytics_password"]
        except KeyError:
            return None

    @staticmethod
    async def get_analytics_login(sender_id: str):
        doc: DocumentSnapshot = firedb.collection(u"users").document(sender_id).get()
        try:
            if doc.exists:
                return doc.to_dict()["data"]["analytics_login"]
        except KeyError:
            return None

    @staticmethod
    async def get_mail_address(sender_id: str):
        doc: DocumentSnapshot = firedb.collection(u"users").document(sender_id).get()
        try:
            if doc.exists:
                return doc.to_dict()["data"]["mail_address"]
        except KeyError:
            return None

    @staticmethod
    async def get_mail_password(sender_id: str):
        doc: DocumentSnapshot = firedb.collection(u"users").document(sender_id).get()
        try:
            if doc.exists:
                return doc.to_dict()["data"]["mail_password"]
        except KeyError:
            return None


class CallbackQueryEventEditors:
    @staticmethod
    async def to_main_page(event: events.CallbackQuery.Event) -> None:
        await event.edit(
            "Choose an option below ↴",
            parse_mode="md",
            buttons=[
                [
                    Button.inline("Schedule »", b"schedule_page")
                ], [
                    Button.inline("Homework »", b"homework_page"),
                ], [
                    Button.inline("Holidays", b"holidays"),
                ], [
                    Button.inline("Marks", b"marks"),
                ]
            ]
        )

    @staticmethod
    async def to_schedule_page(event: events.CallbackQuery.Event) -> None:
        await event.edit(
            "Choose an option below ↴",
            parse_mode="md",
            buttons=[
                [
                    Button.inline("Entire schedule", b"entire_schedule")
                ], [
                    Button.inline("Today's schedule", b"todays_schedule"),
                ], [
                    Button.inline("specific day schedule »", b"specific_day_schedule"),
                ], [
                    Button.inline("« Back", b"main_page")
                ]
            ]
        )

    @staticmethod
    async def to_homework_page(event: events.CallbackQuery.Event) -> None:
        await event.edit(
            "Choose an option below ↴",
            parse_mode="md",
            buttons=[
                [
                    Button.inline("Entire homework", b"entire_homework")
                ], [
                    Button.inline("Tomorrow's homework", b"tomorrows_homework"),
                ], [
                    Button.inline("Specific day homework »", b"specific_day_homework"),
                ], [
                    Button.inline("« Back", b"main_page")
                ]
            ]
        )

    @staticmethod
    async def to_specific_day_schedule_page(event: events.CallbackQuery.Event) -> None:
        await event.edit(
            "Choose a day below ↴",
            parse_mode="md",
            buttons=[
                [
                    Button.inline("Monday", b"monday_schedule")
                ], [
                    Button.inline("Tuesday", b"tuesday_schedule")
                ], [
                    Button.inline("Wednesday", b"wednesday_schedule")
                ], [
                    Button.inline("Thursday", b"thursday_schedule")
                ], [
                    Button.inline("Friday", b"friday_schedule")
                ], [
                    Button.inline("Saturday", b"saturday_schedule")
                ], [
                    Button.inline("« Back", b"schedule_page")
                ]
            ]
        )

    @staticmethod
    async def to_specific_day_homework_page(event: events.CallbackQuery.Event) -> None:
        await event.edit(
            "Choose a day below ↴",
            parse_mode="md",
            buttons=[
                [
                    Button.inline("Monday", b"monday_homework")
                ], [
                    Button.inline("Tuesday", b"tuesday_homework")
                ], [
                    Button.inline("Wednesday", b"wednesday_homework")
                ], [
                    Button.inline("Thursday", b"thursday_homework")
                ], [
                    Button.inline("Friday", b"friday_homework")
                ], [
                    Button.inline("Saturday", b"saturday_homework")
                ], [
                    Button.inline("« Back", b"homework_page")
                ]
            ]
        )


class CallbackQuerySenders:
    def __init__(self, c):
        self.client = c

    async def send_greeting(self, sender) -> None:
        await self.client.send_message(
            entity=sender,
            message=f'Greetings, **{f if (f := sender.first_name) else ""} {l if (l := sender.last_name) else ""}**!',
            parse_mode="md",
            buttons=[
                [
                    Button.text("Options", resize=True, single_use=False)
                ], [
                    Button.text("Clear previous", resize=True, single_use=False)
                ]
            ]
        )

    async def send_init_message(self, sender) -> None:
        await asyncio.sleep(0.1)
        await self.client.send_message(
            entity=sender,
            message=f"I will help you access your schedule via Telegram.\n"
                    "Initially, you should provide your **login** and **password** to"
                    f" [Letovo Analytics]({MAIN_URL_LETOVO}).\n  "
                    f'To do that click the **Log In** button below\n\n'
                    "__After logging into your account, click Options button__",
            parse_mode="md",
            buttons=[
                Button.url(text="Click to log in", url=f'{LOGIN_URL_LOCAL}?chat_id={str(sender.id)}')
            ]
        )

    async def send_main_page(self, sender) -> None:
        await self.client.send_message(
            entity=sender,
            message="Choose an option below ↴",
            parse_mode="md",
            buttons=[
                [
                    Button.inline("Schedule »", b"schedule_page")
                ], [
                    Button.inline("Homework »", b"homework_page"),
                ], [
                    Button.inline("Holidays", b"holidays"),
                ], [
                    Button.inline("Marks", b"marks"),
                ]
            ]
        )

    async def send_holidays(self, sender) -> None:
        await self.client.send_message(
            entity=sender,
            message="__after__ **unit I**\n31.10.2021 — 07.11.2021",
            parse_mode="md"
        )

        await self.client.send_message(
            entity=sender,
            message="__after__ **unit II**\n26.12.2021 — 09.01.2022",
            parse_mode="md"
        )

        await self.client.send_message(
            entity=sender,
            message="__after__ **unit III**\n13.03.2022 — 20.03.2022",
            parse_mode="md"
        )

        await self.client.send_message(
            entity=sender,
            message="__after__ **unit IV**\n22.05.2022 — 31.08.2022",
            parse_mode="md"
        )

    async def send_specific_day_schedule(
            self,
            specific_day: int,
            event: events.CallbackQuery.Event,
            s: FuturesSession,
    ) -> None:
        """
        send schedule for specific day(s)

        :param event: a return object of CallbackQuery
        :param s: requests_futures session
        :param specific_day: day number (-1..5) or (-10) to send entire schedule
        """
        sender = await event.get_sender()
        if specific_day == -1:
            await event.answer("Congrats! It's Sunday, no lessons", alert=False)
            return

        if (schedule := await Web.receive_schedule(s, str(sender.id))) == NameError:
            await event.answer("[✘] Something went wrong!!!", alert=True)
            return

        if not schedule:
            await event.answer("No schedule found in analytics rn", alert=False)
            return

        try:
            await event.answer("", alert=False)
            for ind, day in enumerate(schedule):
                if specific_day in (ind, -10):
                    for lesson in day:
                        await self.client.send_message(
                            entity=sender,
                            message="\n".join(lesson),
                            parse_mode="md",
                            silent=True
                        )
        except Exception as err:
            print(Fg.Red, err, Fg.Reset)
            await event.answer("[✘] Something went wrong!", alert=True)
            return

    async def send_specific_day_homework(self, s: FuturesSession, event: events.CallbackQuery.Event, specific_day: int):
        sender = await event.get_sender()
        student_id, token = await asyncio.gather(
            Firebase.get_student_id(sender_id=str(sender.id)),
            Firebase.get_token(sender_id=str(sender.id))
        )
        homework_url: str = (
            f"https://s-api.letovo.ru/api/schedule/{student_id}/week?schedule_date="
            f"{datetime.datetime.now().date()}"
        )
        homework_headers: dict[str, Optional[str]] = {
            "Authorization": token,
        }
        try:
            homework_future: Future = s.get(url=homework_url, headers=homework_headers)
            if homework_future.result().status_code != 200:
                return None
        except rq.ConnectionError:
            return None

        for day in homework_future.result().json()["data"]:
            if len(day["schedules"]) > 0:
                ch = False
                if int(day["period_num_day"]) == specific_day or specific_day == -10:
                    payload = f'{day["period_name"]}: <strong>{day["schedules"][0]["group"]["subject"]["subject_name_eng"]} {day["schedules"][0]["group"]["group_name"]}</strong>\n' + \
                              f'{Weekdays(int(day["period_num_day"])).name}, {day["date"]}\n'

                    if day["schedules"][0]["lessons"][0]["lesson_hw"]:
                        payload += f'{day["schedules"][0]["lessons"][0]["lesson_hw"]}\n'
                    else:
                        payload += "<em>No homework</em>\n"

                    if day["schedules"][0]["lessons"][0]["lesson_url"]:
                        ch = True
                        payload += f'<a href="{day["schedules"][0]["lessons"][0]["lesson_url"]}">Attached link</a>\n'

                    if day["schedules"][0]["lessons"][0]["lesson_hw_url"]:
                        ch = True
                        payload += f'<a href="{day["schedules"][0]["lessons"][0]["lesson_hw_url"]}">Attached hw link</a>\n'

                    if not ch:
                        payload += "<em>No links attached</em>\n"

                    if day["schedules"][0]["lessons"][0]["lesson_thema"]:
                        payload += f'{day["schedules"][0]["lessons"][0]["lesson_thema"]}\n'
                    else:
                        payload += "<em>No topic</em>\n"

                    await self.client.send_message(
                        entity=sender,
                        message=payload,
                        parse_mode="html",
                        silent=True
                    )


class InlineQueryEventEditors:
    @staticmethod
    async def to_main_page(event: events.InlineQuery.Event) -> None:
        """display main page in inline query"""

        await event.answer(
            results=[
                event.builder.article(
                    title="Holidays",
                    description="send message with vacations terms",
                    text="__after__ **unit I**\n31.10.2021 — 07.11.2021\n\n"
                         "__after__ **unit II**\n26.12.2021 — 09.01.2022\n\n"
                         "__after__ **unit III**\n13.03.2022 — 20.03.2022\n\n"
                         "__after__ **unit IV**\n22.05.2022 — 31.08.2022",
                    thumb=types.InputWebDocument(
                        url="https://letovo-analytics.web.app/static/images/icons/calendar-icon.png",
                        size=512,
                        mime_type="image/jpg",
                        attributes=[
                            types.DocumentAttributeImageSize(
                                w=512,
                                h=512
                            )
                        ]
                    )
                ),
                event.builder.photo(file="static/images/icons/schedule.jpg")
            ], switch_pm="Log in", switch_pm_param="inlineMode"
        )


class InlineQuerySenders:
    @classmethod
    async def send_specific_day_schedule(
            cls,
            specific_day: int,
            event: events.InlineQuery.Event,
            s: FuturesSession,
            sender_id: str
    ) -> Optional[str]:
        """
        send specific day(s) from schedule to inline query

        :param event: a return object of InlineQuery
        :param s: requests_futures session
        :param sender_id: user's telegram id
        :param specific_day: day number (-1..5) or (-10) to send entire schedule
        """
        result = ""
        if specific_day == 0:
            day_name = "Monday"
        elif specific_day == 1:
            day_name = "Tuesday"
        elif specific_day == 2:
            day_name = "Wednesday"
        elif specific_day == 3:
            day_name = "Thursday"
        elif specific_day == 4:
            day_name = "Friday"
        elif specific_day == 5:
            day_name = "Saturday"
        else:
            return

        if specific_day == -1:
            await event.answer(
                results=[
                    event.builder.article(title=f"{day_name} lessons", text="Congrats! It's Sunday, no lessons")
                ], switch_pm="Log in", switch_pm_param="inlineMode"
            )
            return

        if not (schedule := await Web.receive_schedule(s, sender_id)):
            await event.answer(
                results=[
                    event.builder.article(title=f"{day_name} lessons", text="No schedule found in analytics rn")
                ], switch_pm="Log in", switch_pm_param="inlineMode"
            )
            return

        # if schedule == NameError:
        #     await event.answer(
        #         results=[
        #             event.builder.article(title=f"{day_name} lessons", text="[✘] Something went wrong!")
        #         ], switch_pm="Log in", switch_pm_param="inlineMode"
        #     )

        try:
            for ind, day in enumerate(schedule):
                if specific_day in (ind, -10):
                    for lesson in day:
                        result += "\n".join(lesson)
                        result += "\n\n"
            await event.answer(
                results=[
                    event.builder.article(title=f"{day_name} lessons", text=result)
                ], switch_pm="Log in", switch_pm_param="inlineMode"
            )

        except Exception as err:
            log.critical(f"{Fg.Red} {err} {Fg.Reset}")
            await event.answer(
                results=[
                    event.builder.article(title=f"{day_name} lessons", text="[✘] Something went wrong!")
                ], switch_pm="Log in", switch_pm_param="inlineMode"
            )


class Web:
    @staticmethod
    async def receive_token(
            s: FuturesSession, sender_id: str = None, login: str = None, password: str = None
    ) -> Optional[str]:
        if (login is None or password is None) and sender_id is not None:
            login, password = await asyncio.gather(
                Firebase.get_analytics_login(sender_id=sender_id),
                Firebase.get_analytics_password(sender_id=sender_id)
            )
            if not login:
                return

        login_data: dict[str, Optional[str]] = {
            "login": login,
            "password": password
        }
        try:
            login_future: Future = s.post(url=LOGIN_URL_LETOVO, data=login_data)
            for login_futured in as_completed([login_future]):
                login_response = login_futured.result()
                return f'{login_response.json()["data"]["token_type"]} {login_response.json()["data"]["token"]}'
        except rq.ConnectionError:
            return None

    # TODO delete ->
    @staticmethod
    async def receive_token_a(s: FuturesSession, login: str, password: str) -> Optional[str]:
        login_data: dict[str, Optional[str]] = {
            "login": login,
            "password": password
        }
        try:
            login_future: Future = s.post(url=LOGIN_URL_LETOVO, data=login_data)
            for login_futured in as_completed([login_future]):
                login_response = login_futured.result()
                return f'{login_response.json()["data"]["token_type"]} {login_response.json()["data"]["token"]}'
        except rq.ConnectionError:
            return None

    @staticmethod
    async def receive_student_id(s: FuturesSession, sender_id: str) -> Optional[str]:
        me_headers: dict[str, Optional[str]] = {
            "Authorization": await Firebase.get_token(sender_id=sender_id)
        }
        try:
            me_future: Future = s.post("https://s-api.letovo.ru/api/me", headers=me_headers)
            for me_futured in as_completed([me_future]):
                return me_futured.result().json()["data"]["user"]["student_id"]
        except rq.ConnectionError:
            return None

    @staticmethod
    async def receive_student_id_a(s: FuturesSession, token: str) -> Optional[str]:
        me_headers: dict[str, Optional[str]] = {
            "Authorization": token
        }
        try:
            me_future = s.post("https://s-api.letovo.ru/api/me", headers=me_headers)
            for me_futured in as_completed([me_future]):
                return me_futured.result().json()["data"]["user"]["student_id"]
        except rq.ConnectionError:
            return None

    @staticmethod
    async def receive_schedule(s: FuturesSession, sender_id: str):
        student_id, token = await asyncio.gather(
            Firebase.get_student_id(sender_id=sender_id),
            Firebase.get_token(sender_id=sender_id)
        )

        schedule_url: str = (
            f"https://s-api.letovo.ru/api/schedule/{student_id}/week/ics?schedule_date="
            f"{(today := str(datetime.datetime.now().date()))}"
        )
        schedule_headers: dict[str, Optional[str]] = {
            "Authorization": token,
            "schedule_date": today
        }
        try:
            schedule_future: Future = s.get(url=schedule_url, headers=schedule_headers)
            if schedule_future.result().status_code != 200:
                return None
        except rq.ConnectionError:
            return None

        info = []
        ind: int = 0
        day: int = -1
        for ch, e in enumerate(list(Calendar(schedule_future.result().text).timeline)):
            try:
                desc: Any = e.description
            except IndexError:
                desc: str = ""

            if ind != 0 and date != (date := ".".join(reversed(str(e.begin).split("T")[0].split("-")))):
                info.append([])
                day += 1
                ind = 0
            elif ind == 0:
                date: str = ".".join(reversed(str(e.begin).split("T")[0].split("-")))
                info.append([])
                day += 1

            info[day].append([])
            if (name := e.name.split()[0]) == "ММА":
                info[day][ind].append("**ММА**")
            elif name == "Плавание,":
                info[day][ind].append("**Плавание**")
            else:
                lesson = e.name.split("(")[0].split()
                info[day][ind].append(f'{" ".join(lesson[:2])} **{" ".join(lesson[2:])}**')
            if desc:
                if (zoom_url := desc.split("Zoom url:")[-1].strip()) != "no link":
                    info[day][ind].append(f"[ZOOM]({zoom_url})")
                info[day][ind].append(f'{desc.split()[1]} __(Classroom)__')
            info[day][ind].append(
                f'{str(e.begin).split("T")[1].rsplit(":", 2)[0]} — {str(e.end).split("T")[1].rsplit(":", 2)[0]}'
            )
            info[day][ind].append(f'{e.begin.strftime("%A")}, {date}')
            ind += 1
        return info

    # @classmethod
    # async def receive_otp(cls, sender_id: str) -> str:
    #     """not used currently"""
    #     email, password = await asyncio.gather(
    #         Firebase.get_mail_address(sender_id=sender_id),
    #         Firebase.get_mail_password(sender_id=sender_id)
    #     )
    #     mail = IMAP4_SSL("outlook.office365.com")
    #     mail.login(email, password)
    #     mail.list()
    #     mail.select("inbox")
    #     _, data = mail.search(None, "ALL")
    #     _, data = mail.fetch(data[0].split()[-1], "(RFC822)")
    #     otp = message_from_string(data[0][1].decode("utf-8"))
    #     try:
    #         otp = otp.get_payload().split("<b>")[2].split("=")[0].split("<")[0]
    #     except AttributeError:
    #         print(Fg.Blue, otp, Fg.Reset)
    #     return otp


class Database:
    def __init__(self, conn, c):
        self.connection = conn
        self.cursor = c

    async def get_message(self, sender_id: str) -> int:
        with self.connection:
            self.cursor.execute(
                "SELECT message_id FROM messages WHERE sender_id = %s",
                (sender_id,)
            )
            return self.cursor.fetchone()[0]

    async def set_message(self, sender_id: str, message_id: int) -> None:
        with self.connection:
            self.cursor.execute(
                "UPDATE messages SET message_id = %s WHERE sender_id = %s",
                (message_id, sender_id)
            )

    async def is_inited(self, sender_id: str) -> str:
        with self.connection:
            self.cursor.execute(
                "SELECT sender_id FROM messages WHERE sender_id = %s",
                (sender_id,)
            )
            return self.cursor.fetchone()

    async def init_user(self, sender_id: str) -> None:
        with self.connection:
            self.cursor.execute(
                f"INSERT INTO messages (sender_id, message_id) VALUES (%s, %s)",
                (sender_id, None)
            )

    def crate_table(self) -> None:
        with self.connection:
            self.cursor.execute("""
                create table messages (
                    sender_id VARCHAR(255) primary key,
                    message_id INTEGER
                );""")


class Firebase(FirebaseGetters, FirebaseSetters):
    pass


class CallbackQuery(CallbackQueryEventEditors, CallbackQuerySenders):
    pass


class InlineQuery(InlineQueryEventEditors, InlineQuerySenders):
    pass
