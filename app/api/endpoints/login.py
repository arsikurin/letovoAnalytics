import asyncio
import logging as log

import aiohttp
import requests as rq
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse  # , ORJSONResponse HTMLResponse,
from firebase_admin import auth
from requests_futures.sessions import FuturesSession

from app.dependencies import Firebase, Web
from config import settings

router = APIRouter(prefix="/login")
session: aiohttp.ClientSession = ...


@router.on_event("startup")
async def on_startup():
    global session
    session = aiohttp.ClientSession()


@router.on_event("shutdown")
async def on_shutdown():
    await session.close()


@router.post("/")
async def login_api(request: Request):
    try:
        request_data = await request.form()
        analytics_login = request_data.get("login")
        analytics_password = request_data.get("password")
        sender_id = request_data.get("chat_id")
    except KeyError as err:
        raise HTTPException(status_code=422) from err

    login_data = {
        "login": analytics_login,
        "password": analytics_password
    }
    try:
        if not rq.post(url=settings().URL_LOGIN_LETOVO, data=login_data).status_code == 200:
            raise HTTPException(status_code=401)
    except rq.ConnectionError as err:
        raise HTTPException(status_code=502, detail="s.letovo.ru might not responding") from err
    try:
        # with FuturesSession() as session:
        token = await Web.receive_token(session=session, login=analytics_login, password=analytics_password)
        if token == rq.ConnectionError:
            raise HTTPException(status_code=502, detail="s.letovo.ru might not responding")
        try:
            auth.create_user(email=f"{analytics_login}@student.letovo.ru")
        except auth.EmailAlreadyExistsError:
            pass
        await asyncio.gather(
            Firebase.update_data(
                token=token, student_id=await Web.receive_student_id(session=session, token=token),
                analytics_login=analytics_login, analytics_password=analytics_password, sender_id=sender_id,
                lang="en"
            ),
            Firebase.send_email(email=f"{analytics_login}@student.letovo.ru")
        )
        return RedirectResponse(settings().URL_MAIN_LOCAL, status_code=302)
    except Exception as err:
        log.error(err)
        raise HTTPException(status_code=400) from err
