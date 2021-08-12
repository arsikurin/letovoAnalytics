#!/usr/bin/python3.9

import os
# import sys
import asyncio
import sqlite3
import datetime
import time
import requests as rq
import logging as log
import yaml
import firebase_admin

from telethon import Button, events, TelegramClient
from ics import Calendar
from concurrent.futures import as_completed
from requests_futures.sessions import FuturesSession
# from imaplib import IMAP4_SSL
# from bs4 import BeautifulSoup
from colourlib import Fg, Style
from typing import Optional, Any
# from email import message_from_string
from firebase_admin import firestore, credentials

#
# --------------------- Constants
LOGIN_URL_LETOVO = "https://s-api.letovo.ru/api/login"
MAIN_URL_LETOVO = "https://s.letovo.ru"
LOGIN_URL_LOCAL = "https://letovo.cf/login"
# API_ID = 3486313
# API_HASH = "e2e87224f544a2103d75b07e34818563"
# BOT_TOKEN = "1638159959:AAGTSWJV3FGcZLI98WWhKQuIKI1J4NGN_1s"
API_ID = os.environ["API_ID"]
API_HASH = os.environ["API_HASH"]
BOT_TOKEN = os.environ["BOT_TOKEN"]

#
# --------------------- Firestore
firebase_admin.initialize_app(
    credentials.Certificate("fbAdminConfig.json"))
db = firestore.client()

#
# --------------------- Parsing
# soup = BeautifulSoup(html, "lxml")


#
# --------------------- Debug
custom_DEBUG: bool = False
# start_time = time.perf_counter()
# datetime.timedelta(seconds=time.perf_counter() - start_time)

if custom_DEBUG:
    log.basicConfig(
        format=f"{Fg.Green}{Style.Bold}%(asctime)s{Fg.Reset}{Style.Bold} %(message)s{Style.Reset}\n[%(name)s]\n",
        level=log.DEBUG)
else:
    log.basicConfig(
        format=f"{Fg.Green}{Style.Bold}%(asctime)s{Fg.Reset}{Style.Bold} %(message)s{Style.Reset}\n[%(name)s]\n",
        level=log.DEBUG)
    log.getLogger("urllib3.connectionpool").disabled = True
    log.getLogger("asyncio").disabled = True
    log.getLogger("telethon.network.mtprotosender").disabled = True
    log.getLogger("telethon.extensions.messagepacker").disabled = True
    log.getLogger("telethon.client.uploads").disabled = True


# ----------------------------------------------NoSQL funcs-------------------------------------------------------------
async def is_inited(chat_id: str) -> bool:
    docs = db.collection(u"users").stream()
    if chat_id in [doc.id for doc in docs]:
        return True
    return False


async def update_data(
        chat_id: str,
        student_id: int = None,
        mail_address: str = None,
        mail_password: str = None,
        analytics_login: str = None,
        analytics_password: str = None,
        token: str = None
) -> None:
    """Fill out at least one param in every document!!! Otherwise all data in document will be erased"""
    pas = ""
    st = f'"student_id": {student_id},'
    ma = f'"mail_address": "{mail_address}",'
    mp = f'"mail_password": "{mail_password}",'
    al = f'"analytics_login": "{analytics_login}",'
    ap = f'"analytics_password": "{analytics_password}",'
    t = f'"token": "{token}",'

    request_payload: str = '''
    {
        "data": {''' + \
                           f'{st if student_id else pas}' + \
                           f'{ma if mail_address else pas}' + \
                           f'{mp if mail_password else pas}' + \
                           f'{al if analytics_login else pas}' + \
                           f'{ap if analytics_password else pas}' + \
                           f'{t if token else pas}' + \
                           '''},
                           "preferences": {
                               "lang": "en"
                           }
                       }
                       '''
    doc_ref = db.collection(u"users").document(chat_id)
    doc_ref.set(yaml.load(request_payload, Loader=yaml.FullLoader), merge=True)


# --------------------- Getters
async def get_student_id(chat_id: str) -> Optional[int]:
    doc = db.collection(u"users").document(chat_id).get()
    try:
        if doc.exists:
            return doc.to_dict()["data"]["student_id"]
    except KeyError:
        pass
    return None


async def get_token(chat_id: str) -> Optional[str]:
    doc = db.collection(u"users").document(chat_id).get()
    try:
        if doc.exists:
            return doc.to_dict()["data"]["token"]
    except KeyError:
        pass
    return None


async def get_analytics_password(chat_id: str) -> Optional[str]:
    doc = db.collection(u"users").document(chat_id).get()
    try:
        if doc.exists:
            return doc.to_dict()["data"]["analytics_password"]
    except KeyError:
        pass
    return None


async def get_analytics_login(chat_id: str) -> Optional[str]:
    doc = db.collection(u"users").document(chat_id).get()
    try:
        if doc.exists:
            return doc.to_dict()["data"]["analytics_login"]
    except KeyError:
        pass
    return None


async def get_mail_address(chat_id: str) -> Optional[str]:
    doc = db.collection(u"users").document(chat_id).get()
    try:
        if doc.exists:
            return doc.to_dict()["data"]["mail_address"]
    except KeyError:
        pass
    return None


async def get_mail_password(chat_id: str) -> Optional[str]:
    doc = db.collection(u"users").document(chat_id).get()
    try:
        if doc.exists:
            return doc.to_dict()["data"]["mail_password"]
    except KeyError:
        pass
    return None


# -----------------------------------------------SQL funcs--------------------------------------------------------------
async def is_inited_sql(
        chat_id: str,
        conn: sqlite3.Connection,
        c: sqlite3.Cursor
) -> str:
    with conn:
        c.execute("SELECT chat_id FROM messages WHERE chat_id = :chat_id", {"chat_id": chat_id})
        return c.fetchone()


async def init_user_sql(
        chat_id: str,
        conn: sqlite3.Connection,
        c: sqlite3.Cursor
) -> None:
    with conn:
        c.execute("""INSERT INTO messages VALUES (:chat_id, :message_id)""",
                  {"chat_id": chat_id, "message_id": None})


async def set_message_sql(
        chat_id: str,
        message_id: int,
        conn: sqlite3.Connection,
        c: sqlite3.Cursor
) -> None:
    with conn:
        c.execute("UPDATE messages SET message_id = :message_id WHERE chat_id = :chat_id",
                  {"message_id": message_id, "chat_id": chat_id})


async def get_message_sql(
        chat_id: str,
        conn: sqlite3.Connection,
        c: sqlite3.Cursor
) -> int:
    with conn:
        c.execute("SELECT message_id FROM messages WHERE chat_id = :chat_id", {"chat_id": chat_id})
        return c.fetchone()[0]


# ---------------------------------------------Other funcs--------------------------------------------------------------
def is_empty(to_check: Any) -> bool:
    """Dict (map), list (array), tuple, string and None are supported"""
    if not to_check:
        return True
    return False


# --------------------- Receivers
async def receive_token(s: FuturesSession, chat_id: str) -> Optional[str]:
    login, password = await asyncio.gather(get_analytics_login(chat_id=chat_id),
                                           get_analytics_password(chat_id=chat_id))

    login_data: dict[str, Optional[str]] = {
        "login": login,
        "password": password
    }
    try:
        login_future = s.post(url=LOGIN_URL_LETOVO, data=login_data)
        for login_response in as_completed([login_future]):
            return f'{login_response.result().json()["data"]["token_type"]} {login_response.result().json()["data"]["token"]}'
    except rq.ConnectionError:
        return None


async def receive_student_id(s: FuturesSession, chat_id: str) -> Optional[str]:
    me_headers: dict[str, Optional[str]] = {
        "Authorization": await get_token(chat_id=chat_id)
    }
    try:
        me_future = s.post("https://s-api.letovo.ru/api/me", headers=me_headers)
        for me_response in as_completed([me_future]):
            return me_response.result().json()["data"]["user"]["student_id"]
    except rq.ConnectionError:
        return None


async def receive_schedule(s: FuturesSession, chat_id: str) -> Optional[list[list[list[str]]]]:
    student_id, token = await asyncio.gather(get_student_id(chat_id=chat_id),
                                             get_token(chat_id=chat_id))

    schedule_url: str = f"https://s-api.letovo.ru/api/schedule/{student_id}/day/ics?schedule_date=" \
                        f"{(today := str(datetime.datetime.now()).split()[0])}"
    schedule_headers: dict[str, Optional[str]] = {
        "Authorization": token,
        "schedule_date": today
    }
    try:
        schedule_response = s.get(url=schedule_url, headers=schedule_headers)
        if schedule_response.result().status_code != 200:
            return None
    except rq.ConnectionError:
        return None

    info = []
    ind: int = 0
    day: int = -1
    for ch, e in enumerate(list(Calendar(schedule_response.result().text).timeline)):
        try:
            desc: Any = e.description.split()
        except IndexError:
            desc: Any = []

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
        elif name == "Ассамблея,":
            info[day][ind].append("**Ассамблея**")
        else:
            info[day][ind].append(f"**{e.name}**")
        if not is_empty(desc):
            info[day][ind].append(f"[ZOOM]({desc[-1]})")
        info[day][ind].append(f'{e.begin.strftime("%A")}')
        info[day][ind].append(f'{str(e.begin).split("T")[1].rsplit(":", 2)[0]}')
        info[day][ind].append(f'{str(e.end).split("T")[1].rsplit(":", 2)[0]}')
        info[day][ind].append(f"{e.location}")
        info[day][ind].append(f'{date}')
        ind += 1
    return info


async def parse_schedule() -> Optional[list[list[list[str]]]]:
    with open("schedule.ics", "r") as f:
        f = f.read()
    info = []
    ind = 0
    day = -1
    qqq = Calendar(str(f))
    for ch, e in enumerate(list(qqq.timeline)):
        try:
            desc = e.description.split()
        except IndexError:
            desc = []

        if ind != 0 and date != (date := ".".join(reversed(str(e.begin).split("T")[0].split("-")))):
            info.append([])
            day += 1
            ind = 0
        elif ind == 0:
            date = ".".join(reversed(str(e.begin).split("T")[0].split("-")))
            info.append([])
            day += 1

        info[day].append([])
        if (name := e.name.split()[0]) == "ММА":
            info[day][ind].append("**ММА**")
        elif name == "Плавание,":
            info[day][ind].append("**Плавание**")
        elif name == "Ассамблея,":
            info[day][ind].append("**Ассамблея**")
        else:
            info[day][ind].append(f"**{e.name}**")
        if not is_empty(desc):
            info[day][ind].append(f"[ZOOM]({desc[-1]})")
        info[day][ind].append(f'{e.begin.strftime("%A")}')
        info[day][ind].append(f'{str(e.begin).split("T")[1].rsplit(":", 2)[0]}')
        info[day][ind].append(f'{str(e.end).split("T")[1].rsplit(":", 2)[0]}')
        info[day][ind].append(f"{e.location}")
        info[day][ind].append(f'{date}')
        ind += 1
    return info


# async def receive_otp(chat_id: str) -> str:
#     email, password = await asyncio.gather(get_mail_address(chat_id=chat_id),
#                                            get_mail_password(chat_id=chat_id))
#     mail = IMAP4_SSL("outlook.office365.com")
#     mail.login(email, password)
#     mail.list()
#     mail.select("inbox")
#     res, data = mail.search(None, "ALL")
#     res, data = mail.fetch(data[0].split()[-1], "(RFC822)")
#     otp = message_from_string(data[0][1].decode("utf-8"))
#     try:
#         otp = otp.get_payload().split("<b>")[2].split("=")[0].split("<")[0]
#     except AttributeError:
#         print(Fg.Blue, otp, Fg.Reset)
#     return otp


# --------------------- Event editors
async def to_main_page(event: events.CallbackQuery.Event) -> None:
    await event.edit("Choose an option below ↴",
                     parse_mode="md",
                     buttons=[[
                         Button.inline("Schedule »", b"schedule_page")
                     ], [
                         Button.inline("Homework »", b"homework_page"),
                     ], [
                         Button.inline("Holidays", b"holidays"),
                     ], [
                         Button.inline("Marks", b"marks"),
                     ]])


async def to_schedule_page(event: events.CallbackQuery.Event) -> None:
    await event.edit("Choose an option below ↴",
                     parse_mode="md",
                     buttons=[[
                         Button.inline("Entire schedule", b"entire_schedule")
                     ], [
                         Button.inline("Today's schedule", b"todays_schedule"),
                     ], [
                         Button.inline("Certain day schedule »", b"certain_day_schedule"),
                     ], [
                         Button.inline("« Back", b"main_page")
                     ]])


async def to_homework_page(event: events.CallbackQuery.Event) -> None:
    await event.edit("Choose an option below ↴",
                     parse_mode="md",
                     buttons=[[
                         Button.inline("Entire homework", b"entire_homework")
                     ], [
                         Button.inline("Tomorrow's homework", b"tomorrows_homework"),
                     ], [
                         Button.inline("Certain day homework »", b"certain_day_homework"),
                     ], [
                         Button.inline("« Back", b"main_page")
                     ]])


async def to_certain_day_schedule_page(event: events.CallbackQuery.Event) -> None:
    await event.edit("Choose a day below ↴",
                     parse_mode="md",
                     buttons=[[
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
                     ]])


async def to_certain_day_homework_page(event: events.CallbackQuery.Event) -> None:
    await event.edit("Choose a day below ↴",
                     parse_mode="md",
                     buttons=[[
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
                     ]])


# --------------------- Senders
async def send_greeting(client: TelegramClient, sender) -> None:
    await client.send_message(entity=sender,
                              message=f'Greetings, **{fn if (fn := sender.first_name) else ""} {ln if (ln := sender.last_name) else ""}**!',
                              parse_mode="md",
                              buttons=[[
                                  Button.text("Start", resize=True, single_use=False)
                              ], [
                                  Button.text("Clear previous", resize=True, single_use=False)
                              ]])


async def send_init_message(client: TelegramClient, sender) -> None:
    await client.send_message(entity=sender,
                              message=f"I will help you access your schedule via Telegram.\n"
                                      "Initially, you should provide your login and password to"
                                      f" [Letovo Analytics]({MAIN_URL_LETOVO}).\n  "
                                      f'To do that click the button below\n\n'
                                      "__After logging into your account, click Start button again__",
                              parse_mode="md",
                              buttons=[
                                  Button.url(text="Log in", url=f'{LOGIN_URL_LOCAL + "?chat_id=" + str(sender.id)}')
                              ])


async def send_main_page(client: TelegramClient, sender) -> None:
    await client.send_message(entity=sender,
                              message="Choose an option below ↴",
                              parse_mode="md",
                              buttons=[[
                                  Button.inline("Schedule »", b"schedule_page")
                              ], [
                                  Button.inline("Homework »", b"homework_page"),
                              ], [
                                  Button.inline("Holidays", b"holidays"),
                              ], [
                                  Button.inline("Marks", b"marks"),
                              ]])


async def send_holidays(client: TelegramClient, sender) -> None:
    await client.send_message(entity=sender,
                              message="__after__ **I unit**\n31.10.2021 — 07.11.2021",
                              parse_mode="md")

    await client.send_message(entity=sender,
                              message="__after__ **II unit**\n26.12.2021 — 09.01.2022",
                              parse_mode="md")

    await client.send_message(entity=sender,
                              message="__after__ **III unit**\n13.03.2022 — 20.03.2022",
                              parse_mode="md")

    await client.send_message(entity=sender,
                              message="__after__ **IV unit**\n22.05.2022 — 31.08.2022",
                              parse_mode="md")


async def send_specific_day_schedule(
        specific_day: int,
        event: events.CallbackQuery.Event,
        client: TelegramClient,
        s: FuturesSession,
        chat_id: str
) -> None:
    """
    send specific day(s) from schedule

    :param event:
    :param client:
    :param s:
    :param chat_id:
    :param specific_day: day number (-1..5) or (-10) to send entire schedule
    """
    sender = await event.get_sender()
    if specific_day == -1:
        await event.answer("Congrats! It's Sunday, no lessons", alert=False)
        return

    if is_empty(schedule := await receive_schedule(s, chat_id)):
        # if is_empty(schedule := await parse_schedule()):
        await event.answer("No schedule found in analytics rn", alert=False)
        return

    try:
        await event.answer("", alert=False)
        for ind, day in enumerate(schedule):
            if ind == specific_day or specific_day == -10:
                for lesson in day:
                    await client.send_message(entity=sender,
                                              message="\n".join(lesson),
                                              parse_mode="md",
                                              silent=True)
    except Exception as err:
        print(Fg.Red, err, Fg.Reset)
        await event.answer("[✘] Something went wrong!", alert=True)
        return


async def send_specific_day_schedule_inline(
        specific_day: int,
        event: events.InlineQuery.Event,
        s: FuturesSession,
        chat_id: str
) -> Optional[str]:
    """
    send specific day(s) from schedule

    :param event:
    :param s:
    :param chat_id:
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
        await event.answer([
            event.builder.article(title=f"{day_name} lessons",
                                  text="Congrats! It's Sunday, no lessons")
        ], switch_pm="Log in", switch_pm_param="inlineMode")
        return

    if is_empty(schedule := await receive_schedule(s, chat_id)):
        # if is_empty(schedule := await parse_schedule()):
        await event.answer([
            event.builder.article(title=f"{day_name} lessons",
                                  text="No schedule found in analytics rn")
        ], switch_pm="Log in", switch_pm_param="inlineMode")
        return

    try:
        for ind, day in enumerate(schedule):
            if ind == specific_day or specific_day == -10:
                for lesson in day:
                    result += "\n".join(lesson)
                    result += "\n\n"
        await event.answer([
            event.builder.article(title=f"{day_name} lessons", text=result)
        ], switch_pm="Log in", switch_pm_param="inlineMode")

    except Exception as err:
        log.critical(f"{Fg.Red} {err} {Fg.Reset}")
        await event.answer([
            event.builder.article(title=f"{day_name} lessons",
                                  text="[✘] Something went wrong!")
        ], switch_pm="Log in", switch_pm_param="inlineMode")
