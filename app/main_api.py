import essential

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.api.endpoints import login_router, schedule_router
from config import settings

app = FastAPI(
    title=settings().title
)
app.mount("/static", StaticFiles(directory="./app/static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(login_router, tags=["login"])
app.include_router(schedule_router, tags=["schedule"])
