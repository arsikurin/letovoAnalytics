from fastapi import APIRouter, Body, Depends, HTTPException

from app import schemas
from app.api.utils import accept
from config import settings

router = APIRouter(prefix="/schedule")


@router.get("/")
@accept('application/json')
async def read_schedule():
    ...


@read_schedule.accept('text/html')
async def other():
    ...
