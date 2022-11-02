import asyncio
import http
import logging as log
from io import BytesIO

import aiohttp
from fastapi import FastAPI
from fastapi.exceptions import HTTPException, StarletteHTTPException, ValidationError
from fastapi.requests import Request
from fastapi.responses import ORJSONResponse, HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from ics import Calendar

from app.dependencies import API, Firestore, run_parallel, errors as errors_l
from config import settings

api: API
fs: Firestore
app = FastAPI(
    title=settings().title_api,
)

app.mount("/static", StaticFiles(directory="./app/api/static"), name="static")

templates = Jinja2Templates(directory="./app/api/static/templates")
application_json = "application/json"
error_page_t = "pageError.html"


@app.on_event("startup")
async def on_startup():
    global api, fs
    fs = await Firestore.create()
    api = API(session=aiohttp.ClientSession(), fs=fs)


@app.on_event("shutdown")
async def on_shutdown():
    await run_parallel(
        api.session.close(),
        fs.disconnect()
    )


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("indexAPI.html", {"request": request})


@app.get("/ics/{user_id}")
async def webcal_ics(user_id: int):
    try:
        response = await api.receive_schedule_ics(sender_id=str(user_id))
    except (errors_l.UnauthorizedError, errors_l.NothingFoundError, aiohttp.ClientConnectionError) as err:
        log.exception(err)
        raise HTTPException(
            status_code=400, detail=err.__str__(),
            headers={"fix": ""}
        )
    except asyncio.TimeoutError as err:
        log.exception(err)
        raise HTTPException(
            status_code=400, detail=err.__str__(),
            headers={"fix": "Try again later"}
        )

    c = Calendar(response.decode())
    for lesson in c.timeline:
        long_name = lesson.name.split("(")[0].split(":")[-1].strip()
        room = lesson.description.split(";")[0].split("(")[0].split(":")[-1].strip()
        lesson.name = long_name
        lesson.location = room

        link = lesson.description.split(";")[-1].split(":")[-1].strip()
        if link != "no link":
            lesson.description = f"Zoom: {link}"
        else:
            lesson.description = ""

    file = BytesIO(c.serialize().encode())
    file.name = "schedule.ics"

    return StreamingResponse(file, headers={
        "Content-disposition": "attachment; filename=schedule.ics", "Content-type": "text/calendar; charset=utf-8"
    })


@app.exception_handler(StarletteHTTPException)
async def unknown_error(request: Request, error: HTTPException):
    if error.headers is None:
        error.headers = {}

    if error.headers.get("accept") == application_json:
        return ORJSONResponse(
            {"code": error.status_code, "status": "error", "detail": error.detail,
             "fix": error.headers.get("fix") or ""},
            status_code=error.status_code
        )

    return templates.TemplateResponse(
        error_page_t,
        context={"request": request,
                 "error": f"{error.status_code} {error.detail}",
                 "detail": f"[{error.detail if error.detail != http.HTTPStatus(error.status_code).phrase else ''}]",
                 "fix": f"{error.headers.get('fix') or ''}"},
        status_code=error.status_code
    )


@app.exception_handler(ValidationError)
async def validation_error(request: Request, error: ValidationError):
    return ORJSONResponse(error.json(), status_code=400)


@app.exception_handler(500)
async def server_error(request: Request, error: HTTPException):
    log.error(f"{error.__repr__()=} {error.__doc__=}")

    if hasattr(error, "headers") and error.headers is not None:
        headers = error.headers
    else:
        headers = {}

    if hasattr(error, "detail"):
        detail = error.detail
    else:
        detail = http.HTTPStatus(500).phrase

    fix = headers.get("fix") or ""

    if request.headers.get("accept") == application_json:
        return ORJSONResponse(
            {"code": 500, "status": "error", "detail": detail, "fix": fix},
            status_code=500
        )

    return templates.TemplateResponse(
        error_page_t,
        context={
            "request": request,
            "error": "500 Internal Server Error",
            "detail": f"[{detail if detail != http.HTTPStatus(500).phrase else ''}]",
            "fix": fix
        },
        status_code=500
    )


@app.exception_handler(418)
async def im_a_teapot(request: Request, error: HTTPException):
    return templates.TemplateResponse(
        error_page_t,
        context={"request": request,
                 "error": "418 I'm a teapot",
                 "detail": "[This server is a teapot, not a coffee machine]",
                 "fix": ""},
        status_code=418
    )


if __name__ == "__main__":
    import uvicorn

    c = uvicorn.Config(
        app=app, host="0.0.0.0", port=settings().PORT, workers=settings().CONCURRENCY, http="httptools",
        loop="uvloop"
    )  # limit_concurrency

    uvicorn.Server(config=c).run()
