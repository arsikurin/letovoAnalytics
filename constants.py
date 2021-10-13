#!/usr/bin/python3.10

import os

EPS = 2.220446049250313e-16
LOGIN_URL_LETOVO = "https://s-api.letovo.ru/api/login"
MAIN_URL_LETOVO = "https://s.letovo.ru"
MAIN_URL_API = "https://letovo-analytics-api.herokuapp.com/"
LOGIN_URL_LOCAL = "https://letovo-analytics.web.app/login"
GOOGLE_KEY = os.environ["GOOGLE_KEY"]
API_KEY = os.environ["API_KEY"]
API_ID = os.environ["API_ID"]
API_HASH = os.environ["API_HASH"]
BOT_TOKEN = os.environ["BOT_TOKEN"]
HOST_SQL = os.environ["HOST_SQL"]
PORT_SQL = "5432"
USER_SQL = os.environ["USER_SQL"]
DATABASE_SQL = os.environ["DATABASE_SQL"]
PASSWORD_SQL = os.environ["PASSWORD_SQL"]
