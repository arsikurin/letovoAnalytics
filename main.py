# !/usr/bin/python3.9

import sqlite3
import logging as log
import requests as rq
import telethon
import re

from essential import receive_calendar, receive_token, receive_student_id, get_chat_id, init_user, set_analytics_login,\
    set_analytics_password, set_mail_address, set_token, set_student_id

# soup = BeautifulSoup(html, 'lxml')
"https://s-api.letovo.ru/api/students/54405"
"https://s-api.letovo.ru/api/studentsimg/54405"

with sqlite3.connect("users.sql") as conn:
    log.debug("Connected to db")
    c = conn.cursor()
    if not get_chat_id(110011, conn, c):
        init_user(110011, conn, c)
        log.debug("Initialized new user")
    else:
        log.debug("User found")

    with rq.Session() as s:
        if input("reg?"):
            set_analytics_login((a := input("analytics login ->")), 110011, conn, c)
            set_mail_address(f"{a}@student.letovo.ru", 110011, conn, c)
            set_analytics_password(input("analytics password ->"), 110011, conn, c)
            set_token(receive_token(s, 110011, conn, c), 110011, conn, c)
            set_student_id(receive_student_id(s, 110011, conn, c), 110011, conn, c)

        print(receive_calendar(s, 110011, conn, c))
