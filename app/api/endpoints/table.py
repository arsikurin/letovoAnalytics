import asyncio

import aiohttp
from fastapi import APIRouter
from fastapi.requests import Request
from fastapi.templating import Jinja2Templates

from app.api.utils import accept

# from config import settings

router = APIRouter(prefix="/table")
session: aiohttp.ClientSession = ...
templates = Jinja2Templates(directory="./app/api/endpoints/")


@router.on_event("startup")
async def on_startup():
    global session
    session = aiohttp.ClientSession()


@router.on_event("shutdown")
async def on_shutdown():
    await session.close()


@router.get("/")
async def read_table(request: Request):
    users = [
        ("Deutsch", 5, 7, 6, 8, 6, "-", "-", "-", "-", "-", "fin"),
        ("Deutsch", 5, 7, 6, 8, 6, "-", "-", "-", "-", "-", "fin"),
        ("Deutsch", 5, 7, 6, 8, 6, "-", "-", "-", "-", "-", "fin"),
        ("Deutsch", 5, 7, 6, 8, 6, "-", "-", "-", "-", "-", "fin"),
        ("Deutsch", 5, 7, 6, 8, 6, "-", "-", "-", "-", "-", "fin"),
        ("Deutsch", 5, 7, 6, 8, 6, "-", "-", "-", "-", "-", "fin"),
        ("Deutsch", 5, 7, 6, 8, 6, "-", "-", "-", "-", "-", "fin"),
        ("Deutsch", 5, 7, 6, 8, 6, "-", "-", "-", "-", "-", "fin"),
        ("Deutsch", 5, 7, 6, 8, 6, "-", "-", "-", "-", "-", "fin"),
        ("Deutsch", 5, 7, 6, 8, 6, "-", "-", "-", "-", "-", "fin"),
        ("Deutsch", 5, 7, 6, 8, 6, "-", "-", "-", "-", "-", "fin"),
        ("Deutsch", 5, 7, 6, 8, 6, "-", "-", "-", "-", "-", "fin"),
        ("Deutsch", 5, 7, 6, 8, 6, "-", "-", "-", "-", "-", "fin"),
        ("Deutsch", 5, 7, 6, 8, 6, "-", "-", "-", "-", "-", "fin"),
        ("Deutsch", 5, 7, 6, 8, 6, "-", "-", "-", "-", "-", "fin"),
        ("Deutsch", 5, 7, 6, 8, 6, "-", "-", "-", "-", "-", "fin"),
        ("Deutsch", 5, 7, 6, 8, 6, "-", "-", "-", "-", "-", "fin"),
        ("Deutsch", 5, 7, 6, 8, 6, "-", "-", "-", "-", "-", "fin"),
        ("Deutsch", 5, 7, 6, 8, 6, "-", "-", "-", "-", "-", "fin"),
        ("Deutsch", 5, 7, 6, 8, 6, "-", "-", "-", "-", "-", "fin"),
        ("Deutsch", 5, 7, 6, 8, 6, "-", "-", "-", "-", "-", "fin"),
        ("Deutsch", 5, 7, 6, 8, 6, "-", "-", "-", "-", "-", "fin"),
        ("Deutsch", 5, 7, 6, 8, 6, "-", "-", "-", "-", "-", "fin"),
        ("Deutsch", 5, 7, 6, 8, 6, "-", "-", "-", "-", "-", "fin"),
        ("Deutsch", 5, 7, 6, 8, 6, "-", "-", "-", "-", "-", "fin"),
        ("Deutsch", 5, 7, 6, 8, 6, "-", "-", "-", "-", "-", "fin"),

    ]
    return templates.TemplateResponse(
        "bs_table.html",
        context={"request": request,
                 "title": "Academic Performance",
                 "users": users},
        status_code=301
    )
