#!/usr/bin/python3.9

import requests as rq
import logging as log
# import smtplib

from requests_futures.sessions import FuturesSession
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
from firebase_admin._auth_utils import EmailAlreadyExistsError
from threading import Thread
from firebase_admin import auth
from fastapi import FastAPI, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from essential import (
    LOGIN_URL_LETOVO,
    API_KEY,
    Firebase,
    Web
)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


def send_email(email):
    api_url = f"https://www.googleapis.com/identitytoolkit/v3/relyingparty/getOobConfirmationCode?key={API_KEY}"
    headers = {
        "content-type": "application/json; charset=UTF-8"
    }
    data = f'{{"requestType": "PASSWORD_RESET", "email": "{email}"}}'
    request_object = rq.post(api_url, headers=headers, data=data)
    return request_object.json()


# def send_email(analytics_login):
#     with smtplib.SMTP("smtp.gmail.com: 587") as server:
#         msg = MIMEMultipart()
#         password = PASSWORD
#         msg["From"] = "noreply.arseny@gmail.com"
#         msg["To"] = f"{analytics_login}@student.letovo.ru"
#         msg["Subject"] = "Letovo Analytics Bot"
#         msg.attach(MIMEText(f"Successfully logged as {analytics_login} to letovo.cf", "plain"))
#         server.starttls()
#         server.login(msg["From"], password)
#         server.sendmail(msg["From"], msg["To"], msg.as_string())

@app.exception_handler(500)
def unprocessable_entity(request: Request, error):
    log.error(error)
    return templates.TemplateResponse(
        "pageError.html",
        context={"request": request,
                 "error": "500 Internal Server Error",
                 "explain": "",
                 "fix": ""},
        status_code=500
    )


@app.exception_handler(422)
def unprocessable_entity(request: Request, error):
    log.error(error)
    return templates.TemplateResponse(
        "pageError.html",
        context={"request": request,
                 "error": "422 Unprocessable Entity",
                 "explain": "[Possibly missing query string parameters]",
                 "fix": "Use the link that bot provided"},
        status_code=422
    )


@app.exception_handler(418)
def im_a_teapot(request: Request, error):
    log.error(error)
    return templates.TemplateResponse(
        "pageError.html",
        context={"request": request,
                 "error": "418 I'm a teapot",
                 "explain": "[This server is a teapot, not a coffee machine]",
                 "fix": ""},
        status_code=418
    )


@app.exception_handler(405)
def method_not_allowed(request: Request, error):
    log.error(error)
    return templates.TemplateResponse(
        "pageError.html",
        context={"request": request,
                 "error": "405 Method Not Allowed",
                 "explain": "",
                 "fix": ""},
        status_code=405
    )


@app.exception_handler(404)
def not_found(request: Request, error):
    log.error(error)
    return templates.TemplateResponse(
        "pageError.html",
        context={"request": request,
                 "error": "404 Not Found",
                 "explain": "[The page you are looking for does not exist]",
                 "fix": ""},
        status_code=404
    )


@app.exception_handler(403)
def forbidden(request: Request, error):
    log.error(error)
    return templates.TemplateResponse(
        "pageError.html",
        context={"request": request,
                 "error": "403 Forbidden",
                 "explain": "[You have no access to this page]",
                 "fix": ""},
        status_code=403
    )


@app.exception_handler(401)
def unauthorized(request: Request, error):
    log.error(error)
    return templates.TemplateResponse(
        "pageError.html",
        context={"request": request,
                 "error": "401 Unauthorized",
                 "explain": "[Possibly wrong credentials provided]",
                 "fix": ""},
        status_code=401
    )


@app.exception_handler(400)
def bad_request(request: Request, error):
    log.error(error)
    return templates.TemplateResponse(
        "pageError.html",
        context={"request": request,
                 "error": "400 Bad Request",
                 "explain": "",
                 "fix": ""},
        status_code=400
    )


@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse("indexAPI.html", {"request": request})


@app.post("/api/login")
async def login_api(request: Request):
    try:
        request_data = await request.form()
        analytics_login = request_data.get("login")
        analytics_password = request_data.get("password")
        sender_id = request_data.get("chat_id")
    except KeyError:
        return status.HTTP_422_UNPROCESSABLE_ENTITY

    login_data = {
        "login": analytics_login,
        "password": analytics_password
    }
    try:
        if not rq.post(url=LOGIN_URL_LETOVO, data=login_data).status_code == 200:
            return status.HTTP_401_UNAUTHORIZED
    except rq.ConnectionError:
        return status.HTTP_400_BAD_REQUEST  # ConnectionError
    try:
        with FuturesSession() as session:
            token = await Web.receive_token_a(s=session, login=analytics_login, password=analytics_password)
            await Firebase.update_data(
                token=token, student_id=await Web.receive_student_id_a(s=session, token=token),
                analytics_login=analytics_login, analytics_password=analytics_password, sender_id=sender_id, lang="en"
            )
            try:
                auth.create_user(email=f"{analytics_login}@student.letovo.ru")
            except EmailAlreadyExistsError:
                pass
            thread = Thread(target=send_email, daemon=True, args=(f"{analytics_login}@student.letovo.ru",))
            thread.start()
            return RedirectResponse("https://letovo.cf", status_code=302)
    except Exception as err:
        log.debug(err)
        return status.HTTP_400_BAD_REQUEST