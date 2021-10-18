#!/usr/bin/python3.10

import essential
import asyncio
import requests as rq
import logging as log

from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from requests_futures.sessions import FuturesSession
from firebase_admin import auth
from constants import LOGIN_URL_LETOVO
from classes.firebase import Firebase
from classes.web import Web

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.exception_handler(502)
async def bad_gateway(request: Request, error):
    log.error(error)
    return templates.TemplateResponse(
        "pageError.html",
        context={"request": request,
                 "error": "502 Bad Gateway",
                 "explain": "[s.letovo.ru might not responding]",
                 "fix": "Enhance Your Calm"},
        status_code=422
    )


@app.exception_handler(500)
async def server_error(request: Request, error):
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
async def unprocessable_entity(request: Request, error):
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
async def im_a_teapot(request: Request, error):
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
async def method_not_allowed(request: Request, error):
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
async def not_found(request: Request, error):
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
async def forbidden(request: Request, error):
    log.error(error)
    return templates.TemplateResponse(
        "pageError.html",
        context={"request": request,
                 "error": "403 Forbidden",
                 "explain": "[You have no power here, Gandalf the Grey]",
                 "fix": ""},
        status_code=403
    )


@app.exception_handler(401)
async def unauthorized(request: Request, error):
    log.error(error)
    return templates.TemplateResponse(
        "pageError.html",
        context={"request": request,
                 "error": "401 Unauthorized",
                 "explain": "[Possibly wrong credentials provided or your account is blocked]",
                 "fix": "In case your account is blocked, contact Letovo Helpdesk"},
        status_code=401
    )


@app.exception_handler(400)
async def bad_request(request: Request, error):
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
        raise HTTPException(status_code=422)

    login_data = {
        "login": analytics_login,
        "password": analytics_password
    }
    try:
        if not rq.post(url=LOGIN_URL_LETOVO, data=login_data).status_code == 200:
            raise HTTPException(status_code=401)
    except rq.ConnectionError:
        raise HTTPException(status_code=502)
    try:
        with FuturesSession() as session:
            token = await Web.receive_token(s=session, login=analytics_login, password=analytics_password)
            if token == rq.ConnectionError:
                raise HTTPException(status_code=502)
            try:
                auth.create_user(email=f"{analytics_login}@student.letovo.ru")
            except auth.EmailAlreadyExistsError:
                pass
            await asyncio.gather(
                Firebase.update_data(
                    token=token, student_id=await Web.receive_student_id(s=session, token=token),
                    analytics_login=analytics_login, analytics_password=analytics_password, sender_id=sender_id,
                    lang="en"
                ),
                Firebase.send_email(email=f"{analytics_login}@student.letovo.ru")
            )
            return RedirectResponse("https://letovo-analytics.web.app/", status_code=302)
    except Exception as err:
        log.error(err)
        raise HTTPException(status_code=400)
