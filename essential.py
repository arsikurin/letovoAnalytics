#!/usr/bin/python3.10

import os
import re
import yaml
import asyncio
import datetime
import firebase_admin
import requests as rq
import logging as log

# from debug import *
from enum import Enum
from ics import Calendar
from colourlib import Fg, Style
from typing import Optional, Any
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
# TODO marks
# f"https://s-api.letovo.ru/api/schoolprogress/{student_id}?period_num=1"


#
# --------------------- Debug
DEBUG: bool = True
# start_time = time.perf_counter()
# datetime.timedelta(seconds=time.perf_counter() - start_time)

if DEBUG:
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


class NothingFoundError(Exception):
    """
    Occurs when anything cannot by found in the database
    """

    def __init__(self):
        super().__init__(
            "The data you are looking for does not exist"
        )


class UnauthorizedError(Exception):
    """
    Occurs when anything cannot be obtained due to wrong credentials
    """

    def __init__(self):
        super().__init__(
            "The data you are looking cannot be obtained due to wrong credentials"
        )


class Weekdays(Enum):
    Monday = 1
    Tuesday = 2
    Wednesday = 3
    Thursday = 4
    Friday = 5
    Saturday = 6
    ALL = -10


class PatternMatching:
    def __init__(self, s):
        self.today = bool(re.match(r"to", s))
        self.next = bool(re.match(r"ne", s))
        self.monday = bool(re.match(r"mo", s))
        self.tuesday = bool(re.match(r"tu", s))
        self.wednesday = bool(re.match(r"we", s))
        self.thursday = bool(re.match(r"th", s))
        self.friday = bool(re.match(r"fr", s))
        self.saturday = bool(re.match(r"sa", s))
        self.entire = bool(re.match(r"en", s))


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
        doc_ref: DocumentReference = firedb.collection(u"users").document(sender_id)
        doc_ref.set(yaml.full_load(request_payload), merge=True)

    @staticmethod
    async def update_name(
            sender_id: str,
            first_name: Optional[int] = None,
            last_name: Optional[str] = None,
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
        doc_ref: DocumentReference = firedb.collection(u"names").document(sender_id)
        doc_ref.set(yaml.full_load(request_payload), merge=True)


class FirebaseGetters:
    @staticmethod
    async def is_inited(sender_id: str) -> bool:
        docs = firedb.collection(u"users").stream()
        return sender_id in [doc.id for doc in docs]

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
            return NothingFoundError

    @staticmethod
    async def get_token(sender_id: str):
        doc: DocumentSnapshot = firedb.collection(u"users").document(sender_id).get()
        try:
            if doc.exists:
                return doc.to_dict()["data"]["token"]
        except KeyError:
            return NothingFoundError

    @staticmethod
    async def get_analytics_password(sender_id: str):
        doc: DocumentSnapshot = firedb.collection(u"users").document(sender_id).get()
        try:
            if doc.exists:
                return doc.to_dict()["data"]["analytics_password"]
        except KeyError:
            return NothingFoundError

    @staticmethod
    async def get_analytics_login(sender_id: str):
        doc: DocumentSnapshot = firedb.collection(u"users").document(sender_id).get()
        try:
            if doc.exists:
                return doc.to_dict()["data"]["analytics_login"]
        except KeyError:
            return NothingFoundError


class CallbackQueryEventEditors:
    """
    Class for working with callback query events
    """

    @staticmethod
    async def to_main_page(event: events.CallbackQuery.Event):
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
    async def to_schedule_page(event: events.CallbackQuery.Event):
        await event.edit(
            "Choose an option below ↴",
            parse_mode="md",
            buttons=[
                [
                    Button.inline("Entire schedule", b"entire_schedule")
                ], [
                    Button.inline("For Today", b"todays_schedule"),
                ], [
                    Button.inline("Specific day »", b"specific_day_schedule"),
                ], [
                    Button.inline("« Back", b"main_page")
                ]
            ]
        )

    @staticmethod
    async def to_homework_page(event: events.CallbackQuery.Event):
        await event.edit(
            "Choose an option below ↴",
            parse_mode="md",
            buttons=[
                [
                    Button.inline("Entire homework", b"entire_homework")
                ], [
                    Button.inline("For Tomorrow", b"tomorrows_homework"),
                ], [
                    Button.inline("Specific day »", b"specific_day_homework"),
                ], [
                    Button.inline("« Back", b"main_page")
                ]
            ]
        )

    @staticmethod
    async def to_specific_day_schedule_page(event: events.CallbackQuery.Event):
        await event.edit(
            "Choose a day below         ↴",
            parse_mode="md",
            buttons=[
                [
                    Button.inline("Monday", b"monday_schedule"),
                    Button.inline("Tuesday", b"tuesday_schedule")
                ], [
                    Button.inline("Wednesday", b"wednesday_schedule"),
                    Button.inline("Thursday", b"thursday_schedule")
                ], [
                    Button.inline("Friday", b"friday_schedule"),
                    Button.inline("Saturday", b"saturday_schedule")
                ], [
                    Button.inline("« Back", b"schedule_page")
                ]
            ]
        )

    @staticmethod
    async def to_specific_day_homework_page(event: events.CallbackQuery.Event):
        await event.edit(
            "Choose a day below         ↴",
            parse_mode="md",
            buttons=[
                [
                    Button.inline("Monday", b"monday_homework"),
                    Button.inline("Tuesday", b"tuesday_homework")
                ], [
                    Button.inline("Wednesday", b"wednesday_homework"),
                    Button.inline("Thursday", b"thursday_homework")
                ], [
                    Button.inline("Friday", b"friday_homework"),
                    Button.inline("Saturday", b"saturday_homework")
                ], [
                    Button.inline("« Back", b"homework_page")
                ]
            ]
        )


class CallbackQuerySenders:
    def __init__(self, c):
        self.client = c

    async def send_greeting(self, sender):
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

    async def send_init_message(self, sender):
        await asyncio.sleep(0.01)
        await self.client.send_message(
            entity=sender,
            message=f"I will help you access your schedule via Telegram.\n"
                    "Initially, you should provide your **login** and **password** to"
                    f" [Letovo Analytics]({MAIN_URL_LETOVO}).\n  "
                    f'To do that click the **Log In** button below\n\n'
                    "__After logging into your account, click Options button__",
            parse_mode="md",
            buttons=[
                Button.url(text="Click to log in", url=f'{LOGIN_URL_LOCAL}?chat_id={sender.id}')
            ]
        )

    async def send_about_message(self, sender):
        await asyncio.sleep(0.01)
        await self.client.send_message(
            entity=sender,
            message=f"**Arseny Kurin**\n\n"
                    "• 2024kurin.av@student.letovo.ru\n"
                    "• [Github](https://github.com/arsikurin)\n"
                    "• [Telegram](https://t.me/arsikurin)\n",
            parse_mode="md"
        )

    async def send_main_page(self, sender):
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

    async def send_holidays(self, sender):
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
            self, s: FuturesSession, event: events.CallbackQuery.Event, specific_day: int
    ):
        schedule_future = await Web.receive_hw_n_schedule(s, str(event.sender_id))
        if schedule_future == UnauthorizedError:
            return await event.answer("[✘] Cannot get data from s.letovo.ru", alert=True)
        elif schedule_future == NothingFoundError:
            return await event.answer("[✘] Nothing found in database for this user", alert=True)
        elif schedule_future == rq.ConnectionError:
            return await event.answer("[✘] Cannot establish connection to s.letovo.ru", alert=True)

        if specific_day == 0:
            return await event.answer("Congrats! It's Sunday, no lessons", alert=False)

        for day in schedule_future.result().json()["data"]:
            if len(day["schedules"]) > 0:
                if specific_day in (int(day["period_num_day"]), -10):
                    payload = f'{day["period_name"]}: <strong>{day["schedules"][0]["group"]["subject"]["subject_name_eng"]} {day["schedules"][0]["group"]["group_name"]}</strong>\n'

                    if day["schedules"][0]["zoom_meetings"]:
                        payload += f'[ZOOM]({day["schedules"][0]["zoom_meetings"][0]["meeting_url"]}\n)'

                    payload += f'{day["schedules"][0]["room"]["room_name"]} <em>(Classroom)</em>\n'

                    payload += f'{day["period_start"]} — {day["period_end"]}\n'

                    date = day["date"].split("-")
                    payload += f'{Weekdays(int(day["period_num_day"])).name}, {date[2]}.{date[1]}.{date[0]}\n'

                    await self.client.send_message(
                        entity=await event.get_sender(),
                        message=payload,
                        parse_mode="html",
                        silent=True
                    )
        await event.answer()

    async def send_specific_day_homework(
            self, s: FuturesSession, event: events.CallbackQuery.Event, specific_day: int
    ):
        homework_future = await Web.receive_hw_n_schedule(s, str(event.sender_id))
        if homework_future == UnauthorizedError:
            return await event.answer("[✘] Cannot get data from s.letovo.ru", alert=True)
        elif homework_future == NothingFoundError:
            return await event.answer("[✘] Nothing found in database for this user", alert=True)
        elif homework_future == rq.ConnectionError:
            return await event.answer("[✘] Cannot establish connection to s.letovo.ru", alert=True)

        for day in homework_future.result().json()["data"]:
            if len(day["schedules"]) > 0:
                ch = False
                if specific_day in (int(day["period_num_day"]), -10):
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
                        entity=await event.get_sender(),
                        message=payload,
                        parse_mode="html",
                        silent=True
                    )
        await event.answer()


class InlineQueryEventEditors:
    """
    Class for working with inline query events
    """

    @staticmethod
    async def to_main_page(event: events.InlineQuery.Event):
        """
        display main page in inline query
        """

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
        # TODO rewrite
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
            return await event.answer(
                results=[
                    event.builder.article(title=f"{day_name} lessons", text="Congrats! It's Sunday, no lessons")
                ], switch_pm="Log in", switch_pm_param="inlineMode"
            )

        if (schedule := await Web.receive_schedule(s, sender_id)) == rq.ConnectionError:
            return await event.answer(
                results=[
                    event.builder.article(
                        title=f"{day_name} lessons",
                        text="[✘] Cannot establish connection to s.letovo.ru"
                    )
                ], switch_pm="Log in", switch_pm_param="inlineMode"
            )

        if not schedule:
            return await event.answer(
                results=[
                    event.builder.article(
                        title=f"{day_name} lessons",
                        text="No schedule found in analytics rn"
                    )
                ], switch_pm="Log in", switch_pm_param="inlineMode"
            )

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
    ):
        """
        Requires either a sender_id or (password and login)
        """
        if login is None or password is None:
            login, password = await asyncio.gather(
                Firebase.get_analytics_login(sender_id=sender_id),
                Firebase.get_analytics_password(sender_id=sender_id)
            )
            if login == NothingFoundError or password == NothingFoundError:
                return UnauthorizedError

        login_data = {
            "login": login,
            "password": password
        }
        try:
            login_future: Future = s.post(url=LOGIN_URL_LETOVO, data=login_data)
            for login_futured in as_completed([login_future]):
                login_response = login_futured.result()
                return f'{login_response.json()["data"]["token_type"]} {login_response.json()["data"]["token"]}'
        except rq.ConnectionError:
            return rq.ConnectionError

    @staticmethod
    async def receive_student_id(
            s: FuturesSession, sender_id: str = None, token: str = None
    ):
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
            for me_futured in as_completed([me_future]):
                return me_futured.result().json()["data"]["user"]["student_id"]
        except rq.ConnectionError:
            return rq.ConnectionError

    @staticmethod
    async def receive_hw_n_schedule(s: FuturesSession, sender_id: str):
        student_id, token = await asyncio.gather(
            Firebase.get_student_id(sender_id=sender_id),
            Firebase.get_token(sender_id=sender_id)
        )
        if student_id == NothingFoundError or token == NothingFoundError:
            return NothingFoundError

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
    async def receive_schedule(s: FuturesSession, sender_id: str):
        # TODO rewrite
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
                return UnauthorizedError
        except rq.ConnectionError:
            return rq.ConnectionError

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


class Database:
    """
    Class for working with relational DB
    """

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
    """
    Class for working with Firestore DB
    """
    pass


class CallbackQuery(CallbackQueryEventEditors, CallbackQuerySenders):
    """
    Class for working with callback query
    """
    pass


class InlineQuery(InlineQueryEventEditors, InlineQuerySenders):
    """
    Class for working with inline query
    """
    pass
