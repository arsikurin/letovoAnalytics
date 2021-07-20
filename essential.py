# !/usr/bin/python3.9

# import os
# import sys
import sqlite3
import datetime
import time
import requests as rq
import logging as log

from ics import Calendar
from imaplib import IMAP4_SSL
# from bs4 import BeautifulSoup
from colourlib import Fg, Style
from email import message_from_string

LOGIN_URL = "https://s-api.letovo.ru/api/login"
start_time = time.perf_counter()

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


# -----------------------------------------------SQL funcs--------------------------------------------------------------
# def create_table(conn: sqlite3.Connection, c: sqlite3.Cursor) -> None:
#     with conn:
#         c.execute(
#             """CREATE TABLE users (
#                 chat_id INTEGER PRIMARY KEY,
#                 student_id INTEGER,
#                 mail_address VARCHAR (255),
#                 mail_password VARCHAR (255),
#                 analytics_login VARCHAR (255),
#                 analytics_password VARCHAR (255),
#                 token TEXT
#                 )""")


# def clear_db(conn: sqlite3.Connection, c: sqlite3.Cursor) -> None:
#     with conn:
#         c.execute("DELETE FROM users")


# def add_column_to_db(conn: sqlite3.Connection, c: sqlite3.Cursor) -> None:
#     with conn:
#         c.execute("ALTER TABLE users ADD COLUMN name TEXT")


def init_user(chat_id: int, conn: sqlite3.Connection, c: sqlite3.Cursor) -> None:
    with conn:
        c.execute(
            """INSERT INTO users VALUES 
            (:chat_id, :student_id, :mail_address, :mail_password, :analytics_login, :analytics_password, :token)""",
            {"mail_address": None, "mail_password": None, "analytics_password": None, "analytics_login": None,
             "token": None, "student_id": None, "chat_id": chat_id})


def delete_user(chat_id: int, conn: sqlite3.Connection, c: sqlite3.Cursor) -> None:
    with conn:
        c.execute("DELETE FROM users WHERE chat_id = :chat_id", {"chat_id": chat_id})


# --------------------- Setters
def set_student_id(student_id: int, chat_id: int, conn: sqlite3.Connection, c: sqlite3.Cursor) -> None:
    with conn:
        c.execute("UPDATE users SET student_id = :student_id WHERE chat_id = :chat_id",
                  {"student_id": student_id, "chat_id": chat_id})


def set_mail_address(mail_address: str, chat_id: int, conn: sqlite3.Connection, c: sqlite3.Cursor) -> None:
    with conn:
        c.execute("UPDATE users SET mail_address = :mail_address WHERE chat_id = :chat_id",
                  {"mail_address": mail_address, "chat_id": chat_id})


def set_mail_password(mail_password: str, chat_id: int, conn: sqlite3.Connection, c: sqlite3.Cursor) -> None:
    with conn:
        c.execute("UPDATE users SET mail_password = :mail_password WHERE chat_id = :chat_id",
                  {"mail_password": mail_password, "chat_id": chat_id})


def set_analytics_login(analytics_login: str, chat_id: int, conn: sqlite3.Connection, c: sqlite3.Cursor) -> None:
    with conn:
        c.execute("UPDATE users SET analytics_login = :analytics_login WHERE chat_id = :chat_id",
                  {"analytics_login": analytics_login, "chat_id": chat_id})


def set_analytics_password(analytics_password: str, chat_id: int, conn: sqlite3.Connection,
                           c: sqlite3.Cursor) -> None:
    with conn:
        c.execute("UPDATE users SET analytics_password = :analytics_password WHERE chat_id = :chat_id",
                  {"analytics_password": analytics_password, "chat_id": chat_id})


def set_token(token: str, chat_id: int, conn: sqlite3.Connection, c: sqlite3.Cursor) -> None:
    with conn:
        c.execute("UPDATE users SET token = :token WHERE chat_id = :chat_id",
                  {"token": token, "chat_id": chat_id})


# --------------------- Getters
def get_chat_id(chat_id: int, conn: sqlite3.Connection, c: sqlite3.Cursor) -> int:
    with conn:
        c.execute("SELECT chat_id FROM users WHERE chat_id = :chat_id", {"chat_id": chat_id})
        return c.fetchone()[0]


def get_student_id(chat_id: int, conn: sqlite3.Connection, c: sqlite3.Cursor) -> int:
    with conn:
        c.execute("SELECT student_id FROM users WHERE chat_id = :chat_id", {"chat_id": chat_id})
        return c.fetchone()[0]


def get_mail_address(chat_id: int, conn: sqlite3.Connection, c: sqlite3.Cursor) -> str:
    with conn:
        c.execute("SELECT mail_address FROM users WHERE chat_id = :chat_id", {"chat_id": chat_id})
        return c.fetchone()[0]


def get_mail_password(chat_id: int, conn: sqlite3.Connection, c: sqlite3.Cursor) -> str:
    with conn:
        c.execute("SELECT mail_password FROM users WHERE chat_id = :chat_id", {"chat_id": chat_id})
        return c.fetchone()[0]


def get_analytics_login(chat_id: int, conn: sqlite3.Connection, c: sqlite3.Cursor) -> str:
    with conn:
        c.execute("SELECT analytics_login FROM users WHERE chat_id = :chat_id", {"chat_id": chat_id})
        return c.fetchone()[0]


def get_analytics_password(chat_id: int, conn: sqlite3.Connection, c: sqlite3.Cursor) -> str:
    with conn:
        c.execute("SELECT analytics_password FROM users WHERE chat_id = :chat_id", {"chat_id": chat_id})
        return c.fetchone()[0]


def get_token(chat_id: int, conn: sqlite3.Connection, c: sqlite3.Cursor) -> str:
    with conn:
        c.execute("SELECT token FROM users WHERE chat_id = :chat_id", {"chat_id": chat_id})
        return c.fetchone()[0]


# ---------------------------------------------Other funcs--------------------------------------------------------------
def is_empty(tmp) -> bool:
    return len(tmp) == 0


def receive_token(s: rq.Session, chat_id: int, conn: sqlite3.Connection, c: sqlite3.Cursor) -> str:
    login_data = {
        "login": get_analytics_login(chat_id, conn, c),
        "password": get_analytics_password(chat_id, conn, c)
    }
    login_response = s.post(url=LOGIN_URL, data=login_data)
    log.debug(f"Token received in: {datetime.timedelta(seconds=time.perf_counter() - start_time)}")
    return f'{login_response.json()["data"]["token_type"]} {login_response.json()["data"]["token"]}'


def receive_student_id(s: rq.Session, chat_id: int, conn: sqlite3.Connection, c: sqlite3.Cursor) -> int:
    me_headers = {
        "Authorization": get_token(chat_id, conn, c)
    }
    me_response = s.post("https://s-api.letovo.ru/api/me", headers=me_headers)
    log.debug(f"Student id received in: {datetime.timedelta(seconds=time.perf_counter() - start_time)}")
    return me_response.json()["data"]["user"]["student_id"]


def receive_calendar(s: rq.Session, chat_id: int, conn: sqlite3.Connection, c: sqlite3.Cursor) -> list[list]:
    schedule_url = f"https://s-api.letovo.ru/api/schedule/{get_student_id(chat_id, conn, c)}/day/ics?schedule_date=" \
                   f"{(today := str(datetime.datetime.now()).split()[0])}"
    schedule_headers = {
        "Authorization": get_token(chat_id, conn, c),
        "schedule_date": today
    }
    schedule_response = s.get(url=schedule_url, headers=schedule_headers)
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


def get_otp(chat_id: int, conn: sqlite3.Connection, c: sqlite3.Cursor) -> str:
    mail = IMAP4_SSL("outlook.office365.com")
    mail.login(get_mail_address(chat_id, conn, c), get_mail_password(chat_id, conn, c))
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
