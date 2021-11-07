from fastapi import APIRouter, Body, Depends, HTTPException

from app import schemas
from config import settings

router = APIRouter(prefix="/schedule")


@router.get("/")
async def read_schedule():
    ...
