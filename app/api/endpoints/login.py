import logging as log

import aiohttp
from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from fastapi.responses import RedirectResponse  # , ORJSONResponse HTMLResponse,
from firebase_admin import auth

from app.dependencies import Firebase, Web, UnauthorizedError
from config import settings

router = APIRouter(prefix="/login")
session: aiohttp.ClientSession = ...


async def send_email(analytics_login: str):
    try:
        auth.create_user(email=f"{analytics_login}@student.letovo.ru")
    except auth.EmailAlreadyExistsError:
        pass
    await Firebase.send_email(email=f"{analytics_login}@student.letovo.ru")
    return True


@router.on_event("startup")
async def on_startup():
    global session
    session = aiohttp.ClientSession()


@router.on_event("shutdown")
async def on_shutdown():
    await session.close()


@router.post("/")
async def login_api(request: Request, bg: BackgroundTasks):
    try:
        request_data = await request.form()

        analytics_login = request_data["login"]
        analytics_password = request_data["password"]
        sender_id = request_data["sender_id"]
    except KeyError as err:
        raise HTTPException(
            detail="Missing some fields in the request data",
            headers={"fix": "You have to supply login & password & sender_id"},
            status_code=400
        ) from err

    login_data = {
        "login": analytics_login,
        "password": analytics_password
    }
    try:
        async with session.post(url=settings().URL_LOGIN_LETOVO, data=login_data) as resp:
            if resp.status != 200:
                raise HTTPException(
                    status_code=401, detail="Possibly wrong credentials provided or your account is blocked",
                    headers={"fix": "In case your account is blocked, contact Letovo Helpdesk"}
                )
    except aiohttp.ClientConnectionError as err:
        raise HTTPException(
            status_code=502, detail="s.letovo.ru might not responding",
            headers={"fix": ""}
        ) from err

    try:
        token = await Web.receive_token(session=session, login=analytics_login, password=analytics_password)
    except UnauthorizedError as err:
        log.error(err)
        raise HTTPException(
            status_code=400, detail="Cannot get data from s.letovo.ru",
            headers={"fix": ""}
        )
    except aiohttp.ClientConnectionError:
        raise HTTPException(
            status_code=502, detail="s.letovo.ru might not responding",
            headers={"fix": ""}
        )

    try:
        student_id = await Web.receive_student_id(session=session, token=token)
    except UnauthorizedError as err:
        log.error(err)
        raise HTTPException(
            status_code=400, detail="Cannot get data from s.letovo.ru",
            headers={"fix": ""}
        )
    except aiohttp.ClientConnectionError as err:
        log.error(err)
        raise HTTPException(
            status_code=502, detail="Cannot establish connection to s.letovo.ru",
            headers={"fix": ""}
        )

    await Firebase.update_data(
        token=token, student_id=student_id,
        analytics_login=analytics_login, analytics_password=analytics_password, sender_id=sender_id,
        lang="en"
    )
    bg.add_task(send_email, analytics_login)
    return RedirectResponse(settings().URL_MAIN_LOCAL, status_code=302)
