#!/usr/bin/python3.9

# import os
# import sys
import sqlite3
import datetime
import time
import requests as rq
import logging as log
import yaml
import firebase_admin

from telethon import Button
from telethon.client import TelegramClient
from ics import Calendar
# from imaplib import IMAP4_SSL
# from bs4 import BeautifulSoup
from colourlib import Fg, Style
from typing import Optional, Any
# from email import message_from_string
from firebase_admin import firestore, credentials

# Consts
LOGIN_URL_LETOVO = "https://s-api.letovo.ru/api/login"
LOGIN_URL_LOCAL = "https://letovo.cf/login"
API_ID = 3486313
API_HASH = "e2e87224f544a2103d75b07e34818563"
BOT_TOKEN = "1638159959:AAGTSWJV3FGcZLI98WWhKQuIKI1J4NGN_1s"

# Firestore
cred = credentials.Certificate("fbAdminConfig.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

start_time = time.perf_counter()
# soup = BeautifulSoup(html, 'lxml')


custom_DEBUG = False

if custom_DEBUG == "all":
    log.basicConfig(
        format=f"{Fg.Green}{Style.Bold}%(asctime)s{Fg.Reset}{Style.Bold} %(message)s{Style.Reset}\n[%(name)s]\n",
        level=log.DEBUG)
elif custom_DEBUG:
    log.basicConfig(
        format=f"{Fg.Green}{Style.Bold}%(asctime)s{Fg.Reset}{Style.Bold} %(message)s{Style.Reset}\n[%(name)s]\n",
        level=log.DEBUG)
    log.getLogger("urllib3.connectionpool").disabled = True
    log.getLogger("werkzeug").disabled = True


# ----------------------------------------------NoSQL funcs-------------------------------------------------------------
def is_inited(chat_id) -> bool:
    docs = db.collection(u"users").stream()
    if chat_id in [doc.id for doc in docs]:
        return True
    return False


def update_data(
        chat_id: str,
        student_id=None,
        mail_address=None,
        mail_password=None,
        analytics_login=None,
        analytics_password=None,
        token=None
) -> None:
    """Fill out at least one param in every document!!! Otherwise all data in document will be erased"""
    pas = ""
    st = f'"student_id": {student_id},'
    ma = f'"mail_address": "{mail_address}",'
    mp = f'"mail_password": "{mail_password}",'
    al = f'"analytics_login": "{analytics_login}",'
    ap = f'"analytics_password": "{analytics_password}",'
    t = f'"token": "{token}",'

    request_payload = '''
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
def get_student_id(chat_id: str) -> Optional[int]:
    doc = db.collection(u"users").document(chat_id).get()
    try:
        if doc.exists:
            return doc.to_dict()["data"]["student_id"]
    except KeyError:
        pass
    return None


def get_token(chat_id: str) -> Optional[str]:
    doc = db.collection(u"users").document(chat_id).get()
    try:
        if doc.exists:
            return doc.to_dict()["data"]["token"]
    except KeyError:
        pass
    return None


def get_analytics_password(chat_id: str) -> Optional[str]:
    doc = db.collection(u"users").document(chat_id).get()
    try:
        if doc.exists:
            return doc.to_dict()["data"]["analytics_password"]
    except KeyError:
        pass
    return None


def get_analytics_login(chat_id: str) -> Optional[str]:
    doc = db.collection(u"users").document(chat_id).get()
    try:
        if doc.exists:
            return doc.to_dict()["data"]["analytics_login"]
    except KeyError:
        pass
    return None


def get_mail_address(chat_id: str) -> Optional[str]:
    doc = db.collection(u"users").document(chat_id).get()
    try:
        if doc.exists:
            return doc.to_dict()["data"]["mail_address"]
    except KeyError:
        pass
    return None


def get_mail_password(chat_id: str) -> Optional[str]:
    doc = db.collection(u"users").document(chat_id).get()
    try:
        if doc.exists:
            return doc.to_dict()["data"]["mail_password"]
    except KeyError:
        pass
    return None


# -----------------------------------------------SQL funcs--------------------------------------------------------------
def is_inited_sql(
        chat_id: str,
        conn: sqlite3.Connection,
        c: sqlite3.Cursor
) -> str:
    with conn:
        c.execute("SELECT chat_id FROM messages WHERE chat_id = :chat_id", {"chat_id": chat_id})
        return c.fetchone()


def init_user_sql(
        chat_id: str,
        conn: sqlite3.Connection,
        c: sqlite3.Cursor
) -> None:
    with conn:
        c.execute("""INSERT INTO messages VALUES (:chat_id, :message_id)""",
                  {"chat_id": chat_id, "message_id": None})


def set_message_sql(
        chat_id: str,
        message_id: int,
        conn: sqlite3.Connection,
        c: sqlite3.Cursor
) -> None:
    with conn:
        c.execute("UPDATE messages SET message_id = :message_id WHERE chat_id = :chat_id",
                  {"message_id": message_id, "chat_id": chat_id})


def get_message_sql(
        chat_id: str,
        conn: sqlite3.Connection,
        c: sqlite3.Cursor
) -> int:
    with conn:
        c.execute("SELECT message_id FROM messages WHERE chat_id = :chat_id", {"chat_id": chat_id})
        return c.fetchone()[0]


# ---------------------------------------------Other funcs--------------------------------------------------------------
def is_empty(to_check) -> bool:
    """Dict (map), list (array), tuple, string and None are supported"""
    if not to_check:
        return True
    return False


def receive_token(s: rq.Session, chat_id: str) -> Optional[str]:
    login_data = {
        "login": get_analytics_login(chat_id=chat_id),
        "password": get_analytics_password(chat_id=chat_id)
    }
    try:
        login_response: rq.Response = s.post(url=LOGIN_URL_LETOVO, data=login_data)
        return f'{login_response.json()["data"]["token_type"]} {login_response.json()["data"]["token"]}'
    except rq.ConnectionError:
        return None


def receive_student_id(s: rq.Session, chat_id: str) -> Optional[str]:
    me_headers = {
        "Authorization": get_token(chat_id=chat_id)
    }
    try:
        me_response: rq.Response = s.post("https://s-api.letovo.ru/api/me", headers=me_headers)
        return me_response.json()["data"]["user"]["student_id"]
    except rq.ConnectionError:
        return None


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
                                      " [Letovo Analytics](s.letovo.ru).\n  "
                                      f'To do that click the button below\n'
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


async def to_main_page(event) -> None:
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


async def to_schedule_page(event) -> None:
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


async def to_homework_page(event) -> None:
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


async def to_certain_day_schedule_page(event) -> None:
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


async def to_certain_day_homework_page(event) -> None:
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


def receive_schedule(s: rq.Session, chat_id: str) -> Optional[list[list[list[str]]]]:
    schedule_url: str = f"https://s-api.letovo.ru/api/schedule/{get_student_id(chat_id)}/day/ics?schedule_date=" \
                        f"{(today := str(datetime.datetime.now()).split()[0])}"
    schedule_headers: dict[str, Optional[str]] = {
        "Authorization": get_token(chat_id),
        "schedule_date": today
    }
    try:
        schedule_response: rq.Response = s.get(url=schedule_url, headers=schedule_headers)
        if schedule_response.status_code != 200:
            return None
    except rq.ConnectionError:
        return None

    info = []
    ind: int = 0
    day: int = -1
    for ch, e in enumerate(list(Calendar(schedule_response.text).timeline)):
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


def parse_schedule() -> Optional[list[list[list[str]]]]:
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


# def get_otp(chat_id: str) -> str:
#     mail = IMAP4_SSL("outlook.office365.com")
#     mail.login(get_mail_address(chat_id=chat_id), get_mail_password(chat_id=chat_id))
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


async def send_certain_day_schedule(
        day: int,
        event,
        client: TelegramClient,
        s: rq.Session,
        chat_id: str
) -> None:
    """
    send certain day from schedule

    :param event:
    :param client:
    :param s:
    :param chat_id:
    :param day: day number (-1..5) or (-10) to send entire schedule
    """

    sender = await event.get_sender()
    if day == -1:
        await event.answer("Congrats! It's Sunday, no lessons", alert=False)
        return

    # if is_empty(schedule := receive_schedule(s, chat_id)):
    if is_empty(schedule := parse_schedule()):
        await event.answer("No schedule found in analytics rn", alert=False)
        return

    try:
        await event.answer("", alert=False)
        for ind, day in enumerate(schedule):
            if ind == day or day == -10:
                for lesson in day:
                    await client.send_message(entity=sender,
                                              message="\n".join(lesson),
                                              parse_mode="md",
                                              silent=True)
    except Exception as err:
        print(Fg.Red, err, Fg.Reset)
        await event.answer("[✘] Something went wrong!", alert=True)
        return
