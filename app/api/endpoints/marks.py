import asyncio

import aiohttp
from fastapi import APIRouter, HTTPException, Header  # Body, Depends,
from fastapi.requests import Request
from fastapi.responses import ORJSONResponse  # HTMLResponse,

from app.api.utils import accept
from app.dependencies import Firebase, NothingFoundError
from app.schemas import MarksResponse

# from config import settings

router = APIRouter(prefix="/marks")
session: aiohttp.ClientSession = ...


@router.on_event("startup")
async def on_startup():
    global session
    session = aiohttp.ClientSession()


@router.on_event("shutdown")
async def on_shutdown():
    await session.close()


@router.get("/", response_model=MarksResponse, response_class=ORJSONResponse)
@accept("application/json")
async def read_marks(request: Request, sender_id=Header(...)):
    student_id, token = await asyncio.gather(
        Firebase.get_student_id(sender_id=sender_id),
        Firebase.get_token(sender_id=sender_id)
    )
    if NothingFoundError in (student_id, token):
        raise HTTPException(
            403, detail="Nothing found in the database for this user",
            headers={"fix": "You should be registered in the bot"}
        )

    # TODO period_num
    url = f"https://s-api.letovo.ru/api/schoolprogress/{student_id}?period_num=1"
    headers = {
        "Authorization": token,
    }

    try:
        async with session.get(url=url, headers=headers) as resp:
            if resp.status != 200:
                raise HTTPException(resp.status, detail="Cannot get data from s.letovo.ru")
            return await resp.json()
    except aiohttp.ClientConnectionError as err:
        raise HTTPException(
            status_code=502, detail="Cannot establish connection to s.letovo.ru",
            headers={"fix": "Enhance Your Calm"}
        ) from err