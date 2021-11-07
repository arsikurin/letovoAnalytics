import asyncio
import requests as rq
import logging as log

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, ORJSONResponse
from requests_futures.sessions import FuturesSession
from firebase_admin import auth
from app.dependencies import Firebase, Web
from config import settings

router = APIRouter(prefix="/login")


@router.post("/")
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
        if not rq.post(url=settings().URL_LOGIN_LETOVO, data=login_data).status_code == 200:
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
            return RedirectResponse(settings().URL_MAIN_LOCAL, status_code=302)
    except Exception as err:
        log.error(err)
        raise HTTPException(status_code=400)
