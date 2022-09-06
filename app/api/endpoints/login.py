import datetime
import logging as log
import time

import aiohttp
from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from fastapi.responses import RedirectResponse
from firebase_admin import auth

from app.dependencies import Firestore, Web, errors as errors_l, run_parallel
from config import settings

router = APIRouter(prefix="/login")
web: Web
fs: Firestore


async def send_email(analytics_login: str, sender_id: str) -> bool:
    if fs.is_logged(sender_id=sender_id):
        try:
            auth.create_user(email=f"{analytics_login}@student.letovo.ru")
        except auth.EmailAlreadyExistsError:
            pass
        await fs.send_email_to(f"{analytics_login}@student.letovo.ru")
    else:
        # TODO error handler
        ...
    return True


@router.on_event("startup")
async def on_startup():
    global web, fs
    fs = await Firestore.create()
    web = Web(session=aiohttp.ClientSession(), fs=fs)


@router.on_event("shutdown")
async def on_shutdown():
    await run_parallel(
        web.session.close(),
        fs.disconnect()
    )


@router.get("/")
async def login_api(request: Request, bg: BackgroundTasks):
    # try:
    #     request_data = await request.form()
    #
    #     analytics_login = request_data["login"]
    #     analytics_password = request_data["password"]
    #     sender_id = request_data["sender_id"]
    # except KeyError as err:
    #     raise HTTPException(
    #         detail="Missing some fields in the request data",
    #         headers={"fix": "You have to supply login & password & sender_id"},
    #         status_code=400
    #     ) from err
    analytics_login = "2024kurin.av"
    analytics_password = "Gas92753"
    sender_id = "665544"
    login_data = {
        "login": analytics_login,
        "password": analytics_password
    }
    try:
        async with web.session.post(url=settings().URL_LOGIN_LETOVO, data=login_data) as resp:
            if resp.status != 200:
                raise HTTPException(
                    status_code=401, detail="Possibly wrong credentials provided or your account is blocked",
                    headers={"fix": "In case your account is blocked, contact Letovo Helpdesk"}
                )
    except aiohttp.ClientConnectionError as err:
        raise HTTPException(
            status_code=502, detail="Cannot establish connection to s.letovo.ru",
            headers={"fix": ""}
        ) from err

    start_time1 = time.perf_counter()
    try:
        token = await web.receive_token(login=analytics_login, password=analytics_password)
    except errors_l.UnauthorizedError as err:
        log.error(err)
        raise HTTPException(
            status_code=400, detail="Cannot get data from s.letovo.ru",
            headers={"fix": ""}
        )
    except aiohttp.ClientConnectionError:
        raise HTTPException(
            status_code=502, detail="Cannot establish connection to s.letovo.ru",
            headers={"fix": ""}
        )

    try:
        student_id = await web.receive_student_id(token=token)
    except errors_l.UnauthorizedError as err:
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

    # await fs.update_data(
    #     token=token, student_id=student_id,
    #     analytics_login=analytics_login, analytics_password=analytics_password, sender_id=sender_id,
    #     lang="en"
    # )
    bg.add_task(
        fs.update_data, token=token, student_id=student_id,
        analytics_login=analytics_login, analytics_password=analytics_password, sender_id=sender_id,
        lang="en"
    )
    bg.add_task(send_email, analytics_login=analytics_login, sender_id=sender_id)
    print("LAYER ALL", datetime.timedelta(seconds=time.perf_counter() - start_time1))
    return RedirectResponse(settings().URL_MAIN_LOCAL, status_code=302)
