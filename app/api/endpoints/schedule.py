import asyncio
import datetime

import aiohttp
from fastapi import APIRouter, HTTPException, Header  # Body, Depends,
from fastapi.requests import Request
from fastapi.responses import ORJSONResponse  # HTMLResponse,

from app.api.utils import accept
from app.dependencies import Firestore, NothingFoundError
from app.schemas import ScheduleResponse

# from config import settings

router = APIRouter(prefix="/schedule")
session: aiohttp.ClientSession = ...
fs: Firestore = ...


@router.on_event("startup")
async def on_startup():
    global session, fs
    session = aiohttp.ClientSession()
    fs = await Firestore.create()


@router.on_event("shutdown")
async def on_shutdown():
    await session.close()


@router.get("/", response_model=ScheduleResponse, response_class=ORJSONResponse)
@accept("application/json")
async def read_schedule(request: Request, sender_id=Header(...)):
    student_id, token = await asyncio.gather(
        fs.get_student_id(sender_id=sender_id),
        fs.get_token(sender_id=sender_id)
    )
    if NothingFoundError in (student_id, token):
        raise HTTPException(
            403, detail="Nothing found in the database for this user",
            headers={"fix": "You should be registered in the bot"}
        )

    url = (
        f"https://s-api.letovo.ru/api/schedule/{student_id}/week?schedule_date="
        f"{datetime.datetime.now().date()}"
    )
    headers = {
        "Authorization": token,
    }

    try:
        async with session.get(url, headers=headers) as resp:
            if resp.status != 200:
                raise HTTPException(403, detail="Cannot get data from s.letovo.ru")
            return await resp.json()
    except aiohttp.ClientConnectionError as err:
        raise HTTPException(
            status_code=502, detail="Cannot establish connection to s.letovo.ru",
            headers={"fix": "Enhance Your Calm"}
        ) from err
