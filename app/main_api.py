import asyncio
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

# noinspection PyUnresolvedReferences
import essential
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
async def lol(user_id: int):
    try:
        response = await api.receive_schedule_ics(sender_id=str(user_id))
    except (errors_l.UnauthorizedError, errors_l.NothingFoundError, aiohttp.ClientConnectionError) as err:
        log.error(err)
        raise HTTPException(
            status_code=400, detail=err.__str__(),
            headers={"fix": ""}
        )
    except asyncio.TimeoutError as err:
        log.error(err)
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
    if hasattr(error, "headers"):
        if error.headers is None:
            error.headers = {}
        return ORJSONResponse(
            {"code": error.status_code, "status": "error", "detail": error.detail, "fix": error.headers.get("fix")},
            status_code=error.status_code
        )
    return ORJSONResponse(
        {"code": error.status_code, "status": "error", "detail": error.detail},
        status_code=error.status_code
    )


@app.exception_handler(ValidationError)
async def validation_error(request: Request, error: ValidationError):
    return ORJSONResponse(error.json(), status_code=400)


@app.exception_handler(502)
async def bad_gateway(request: Request, error: HTTPException):
    if error.headers is None:
        error.headers = {}
    if request.headers.get("accept") == application_json:
        return ORJSONResponse(
            {"code": error.status_code, "status": "error", "detail": error.detail, "fix": error.headers.get("fix")},
            status_code=error.status_code
        )
    else:
        return templates.TemplateResponse(
            error_page_t,
            context={"request": request,
                     "error": "502 Bad Gateway",
                     "detail": f"[{error.detail}]",
                     "fix": f"{error.headers.get('fix')}"},
            status_code=502
        )


@app.exception_handler(500)
async def server_error(request: Request, error: HTTPException):
    if isinstance(error, HTTPException):
        if error.headers is None:
            error.headers = {}
        if request.headers.get("accept") == application_json:
            return ORJSONResponse(
                {"code": error.status_code, "status": "error", "detail": error.detail, "fix": error.headers.get("fix")},
                status_code=error.status_code
            )
        else:
            return templates.TemplateResponse(
                error_page_t,
                context={"request": request,
                         "error": "500 Internal Server Error"},
                status_code=500
            )
    if request.headers.get("accept") == application_json:
        return ORJSONResponse(
            {"code": 500, "status": "error", "detail": error.__repr__(), "doc": error.__doc__},
            status_code=500
        )
    else:
        return templates.TemplateResponse(
            error_page_t,
            context={"request": request,
                     "error": "500 Internal Server Error"},
            status_code=500
        )


@app.exception_handler(422)
async def unprocessable_entity(request: Request, error: HTTPException):
    if error.headers is None:
        error.headers = {}
    if request.headers.get("accept") == application_json:
        return ORJSONResponse(
            {"code": error.status_code, "status": "error", "detail": error.detail, "fix": error.headers.get("fix")},
            status_code=error.status_code
        )
    else:
        return templates.TemplateResponse(
            error_page_t,
            context={"request": request,
                     "error": "422 Unprocessable Entity",
                     "detail": f"[{error.detail}]",  # [Possibly missing query string parameters]
                     "fix": f"{error.headers.get('fix')}"},  # Use the link that bot provided
            status_code=422
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


@app.exception_handler(404)
async def not_found(request: Request, error: HTTPException):
    if request.headers.get("accept") == application_json:
        if hasattr(error, "headers"):
            return ORJSONResponse(
                {"code": 404, "status": "error", "detail": error.detail, "fix": error.headers.get("fix")},
                status_code=404
            )
        else:
            return ORJSONResponse(
                {"code": 404, "status": "error", "detail": error.detail},
                status_code=404
            )
    else:
        if error.detail != "Not Found":
            return templates.TemplateResponse(
                error_page_t,
                context={"request": request,
                         "error": "404 Not Found",
                         "detail": f"[{error.detail}]"},
                status_code=404
            )
        else:
            return templates.TemplateResponse(
                error_page_t,
                context={"request": request,
                         "error": "404 Not Found",
                         "detail": "[The page you are looking for does not exist]"},
                status_code=404
            )


@app.exception_handler(403)
async def forbidden(request: Request, error: HTTPException) -> templates.TemplateResponse:
    if error.headers is None:
        error.headers = {}
    if request.headers.get("accept") == application_json:
        return ORJSONResponse(
            {"code": error.status_code, "status": "error", "detail": error.detail, "fix": error.headers.get("fix")},
            status_code=error.status_code
        )
    else:
        return templates.TemplateResponse(
            error_page_t,
            context={"request": request,
                     "error": "403 Forbidden",
                     "detail": f"[{error.detail}]",  # [You have no power here, Gandalf the Grey]
                     "fix": f"{error.headers.get('fix')}"},
            status_code=403
        )


@app.exception_handler(401)
async def unauthorized(request: Request, error: HTTPException) -> templates.TemplateResponse:
    if error.headers is None:
        error.headers = {}
    if request.headers.get("accept") == application_json:
        return ORJSONResponse(
            {"code": error.status_code, "status": "error", "detail": error.detail, "fix": error.headers.get("fix")},
            status_code=error.status_code
        )
    else:
        return templates.TemplateResponse(
            error_page_t,
            context={"request": request,
                     "error": "401 Unauthorized",
                     "detail": f"[{error.detail}]",
                     # [Possibly wrong credentials provided or your account is blocked]
                     "fix": f"{error.headers.get('fix')}"},
            # In case your account is blocked, contact Letovo Helpdesk
            status_code=401
        )


@app.exception_handler(400)
async def bad_request(request: Request, error: HTTPException) -> templates.TemplateResponse:
    if error.headers is None:
        error.headers = {}
    if request.headers.get("accept") == application_json:
        return ORJSONResponse(
            {"code": error.status_code, "status": "error", "detail": error.detail, "fix": error.headers.get("fix")},
            status_code=error.status_code
        )
    else:
        return templates.TemplateResponse(
            error_page_t,
            context={"request": request,
                     "error": "400 Bad Request",
                     "detail": f"[{error.detail}]",
                     "fix": f"{error.headers.get('fix')}"},
            status_code=400
        )


if __name__ == "__main__":
    import uvicorn

    c = uvicorn.Config(
        app=app, host="0.0.0.0", port=settings().PORT, workers=settings().WEB_CONCURRENCY, http="httptools",
        loop="uvloop"
    )  # limit_concurrency

    uvicorn.Server(config=c).run()
