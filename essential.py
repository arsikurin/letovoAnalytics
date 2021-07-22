#!/usr/bin/python3.9

# import os
# import sys
# import sqlite3
import datetime
import time
import requests as rq
import logging as log
# import json
import yaml
import firebase_admin

from ics import Calendar
from imaplib import IMAP4_SSL
# from bs4 import BeautifulSoup
from colourlib import Fg, Style
from typing import Optional, Any
from email import message_from_string
from firebase_admin import firestore, credentials

# Consts
LOGIN_URL_LETOVO = "https://s-api.letovo.ru/api/login"
LOGIN_URL_LOCAL = "https://letovo-analytics-test.herokuapp.com//login"
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
        chat_id,
        student_id=None,
        mail_address=None,
        mail_password=None,
        analytics_login=None,
        analytics_password=None,
        token=None
):
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
    doc_ref = db.collection(u'users').document(chat_id)
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


# ---------------------------------------------Other funcs--------------------------------------------------------------
def is_empty(tmp) -> bool:
    if not tmp:
        return True
    return False


def receive_token(s: rq.Session, chat_id: str) -> Optional[str]:
    login_data = {
        "login": get_analytics_login(chat_id),
        "password": get_analytics_password(chat_id)
    }
    try:
        login_response = s.post(url=LOGIN_URL_LETOVO, data=login_data)
        log.debug(f"Token received in: {datetime.timedelta(seconds=time.perf_counter() - start_time)}")
        return f'{login_response.json()["data"]["token_type"]} {login_response.json()["data"]["token"]}'
    except rq.ConnectionError:
        return None


def receive_student_id(s: rq.Session, chat_id: str) -> Optional[str]:
    me_headers = {
        "Authorization": get_token(chat_id)
    }
    try:
        me_response = s.post("https://s-api.letovo.ru/api/me", headers=me_headers)
        log.debug(f"Student id received in: {datetime.timedelta(seconds=time.perf_counter() - start_time)}")
        return me_response.json()["data"]["user"]["student_id"]
    except rq.ConnectionError:
        return None


def receive_calendar(s: rq.Session, chat_id: str) -> Optional[list[list]]:
    schedule_url = f"https://s-api.letovo.ru/api/schedule/{get_student_id(chat_id)}/day/ics?schedule_date=" \
                   f"{(today := str(datetime.datetime.now()).split()[0])}"
    schedule_headers = {
        "Authorization": get_token(chat_id),
        "schedule_date": today
    }
    try:
        schedule_response = s.get(url=schedule_url, headers=schedule_headers)
    except rq.ConnectionError:
        return None
    log.debug(f"Calendar received in: {datetime.timedelta(seconds=time.perf_counter() - start_time)}")

    info = []
    ind = 0
    day = -1
    for ch, e in enumerate(list(Calendar(schedule_response.text).timeline)):
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
            info[day][ind].append("*ММА*")
        elif name == "Плавание,":
            info[day][ind].append("*Плавание*")
        elif name == "Ассамблея,":
            info[day][ind].append("*Ассамблея*")
        else:
            info[day][ind].append(f"*{e.name}*")
        if not is_empty(desc):
            info[day][ind].append(f"[ZOOM]({desc[-1]})")
        info[day][ind].append(f'*{e.begin.strftime("%A")}*')
        info[day][ind].append(f'*{str(e.begin).split("T")[1].rsplit(":", 2)[0]}*')
        info[day][ind].append(f'*{str(e.end).split("T")[1].rsplit(":", 2)[0]}*')
        info[day][ind].append(f"*{e.location}*")
        info[day][ind].append(f'*{date}*')
        ind += 1
    log.debug(f"Calendar parsed in: {datetime.timedelta(seconds=time.perf_counter() - start_time)}")
    return info


def get_otp(chat_id: str) -> str:
    mail = IMAP4_SSL("outlook.office365.com")
    mail.login(get_mail_address(chat_id), get_mail_password(chat_id))
    mail.list()
    mail.select("inbox")
    res, data = mail.search(None, "ALL")
    res, data = mail.fetch(data[0].split()[-1], "(RFC822)")
    otp = message_from_string(data[0][1].decode("utf-8"))
    try:
        otp = otp.get_payload().split("<b>")[2].split("=")[0].split("<")[0]
    except AttributeError:
        print(Fg.Blue, otp, Fg.Reset)
    return otp

# def send_certain_day_calendar(certain_day: int, call) -> None:
#     """
#     send certain day from calendar
#
#     :param certain_day: day number (0-6)
#     """
#     from main import bot
#
#     markup = generate_reply_keyboard(start=0)
#     bot.answer_callback_query(callback_query_id=call.id, show_alert=True, text="Wait 6 secs")
#     bot.delete_message(call.message.chat.id, call.message.message_id)
#
#     if int(certain_day) == -1:
#         bot.send_message(call.message.chat.id, "_Congrats! It's Sunday, no lessons_", parse_mode="Markdown",
#                          reply_markup=markup)
#         keyboard = generate_inline_keyboard(authorization="Edit authorization data »",
#                                             currentDayCalendar="Current day calendar",
#                                             entireCalendar="Entire calendar",
#                                             certainDayCalendar="Certain day calendar »")
#         bot.send_message(call.message.chat.id, "Choose an option below ↴", reply_markup=keyboard)
#     else:
#         try:
#             for ind, day in enumerate(receive_calendar(call)):
#                 if ind == certain_day or certain_day == -10:
#                     for lesson in day:
#                         bot.send_message(call.message.chat.id, "\n".join(lesson), parse_mode="Markdown",
#                                          reply_markup=markup, disable_notification=True)
#         except Exception as err:
#             print(Fg.Red, err, Fg.Reset)
#             bot.send_message(call.message.chat.id, "_✗ Something went wrong! Try again in 3 secs ✗_",
#                              parse_mode="Markdown", reply_markup=markup)
#             bot.answer_callback_query(callback_query_id=call.id, show_alert=True,
#                                       text="✗ Something went wrong! Try again in 3 secs ✗")
#             keyboard = generate_inline_keyboard(authorization="Edit authorization data »",
#                                                 currentDayCalendar="Current day calendar",
#                                                 entireCalendar="Entire calendar",
#                                                 certainDayCalendar="Certain day calendar »")
#             bot.send_message(call.message.chat.id, "Choose an option below ↴", reply_markup=keyboard)


# def send_certain_day_homework(certain_day: int, call):
#     from main import bot
#
#     markup = generate_reply_keyboard(start=0)
#     bot.answer_callback_query(callback_query_id=call.id, show_alert=True, text="Wait 6 secs")
#     bot.delete_message(call.message.chat.id, call.message.message_id)
#
#     if int(certain_day) == -1:
#         bot.send_message(call.message.chat.id, "_Congrats! Tomorrow is Sunday, no homework_", parse_mode="Markdown",
#                          reply_markup=markup)
#         keyboard = generate_inline_keyboard(authorization="Edit authorization data »",
#                                             currentDayCalendar="Current day calendar",
#                                             entireCalendar="Entire calendar",
#                                             certainDayCalendar="Certain day calendar »")
#         bot.send_message(call.message.chat.id, "Choose an option below ↴", reply_markup=keyboard)
#     else:
#         with open("homework.html", "w") as f:
#             f.write(get_homework(call))
#             print(Fg.Blue, "OK!!!", Fg.Reset)
