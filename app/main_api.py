#!/usr/bin/python3.10

import essential
import aiohttp
from fastapi import FastAPI
from fastapi.exceptions import HTTPException, StarletteHTTPException, ValidationError
from fastapi.requests import Request
from fastapi.responses import ORJSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.endpoints import login_router, schedule_router
from config import settings

session: aiohttp.ClientSession = ...
app = FastAPI(
    title=settings().title
)

app.mount("/static", StaticFiles(directory="./app/static"), name="static")
templates = Jinja2Templates(directory="./app/templates")
app.include_router(login_router, tags=["login"])
app.include_router(schedule_router, tags=["schedule"])


@app.on_event("startup")
async def on_startup():
    global session
    session = aiohttp.ClientSession()


@app.on_event("shutdown")
async def on_shutdown():
    await session.close()


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("indexAPI.html", {"request": request})


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
    if request.headers.get("accept") == "application/json":
        return ORJSONResponse(
            {"code": error.status_code, "status": "error", "detail": error.detail, "fix": error.headers.get("fix")},
            status_code=error.status_code
        )
    else:
        return templates.TemplateResponse(
            "pageError.html",
            context={"request": request,
                     "error": "502 Bad Gateway",
                     "detail": f"[{error.detail}]",
                     "fix": f"{error.headers.get('fix')}"},
            status_code=502
        )


@app.exception_handler(500)
async def bad_gateway(request: Request, error: HTTPException):
    if isinstance(error, HTTPException):
        if error.headers is None:
            error.headers = {}
        if request.headers.get("accept") == "application/json":
            return ORJSONResponse(
                {"code": error.status_code, "status": "error", "detail": error.detail, "fix": error.headers.get("fix")},
                status_code=error.status_code
            )
        else:
            return templates.TemplateResponse(
                "pageError.html",
                context={"request": request,
                         "error": "500 Internal Server Error",
                         "detail": f"[{error.detail}]",
                         "fix": f"{error.headers.get('fix')}"},
                status_code=500
            )
    if request.headers.get("accept") == "application/json":
        return ORJSONResponse(
            {"code": 500, "status": "error", "detail": error.__str__()},
            status_code=500
        )
    else:
        return templates.TemplateResponse(
            "pageError.html",
            context={"request": request,
                     "error": "500 Internal Server Error",
                     "detail": f"[{error.__str__()}]"},
            status_code=500
        )


@app.exception_handler(422)
async def unprocessable_entity(request: Request, error: HTTPException):
    if error.headers is None:
        error.headers = {}
    if request.headers.get("accept") == "application/json":
        return ORJSONResponse(
            {"code": error.status_code, "status": "error", "detail": error.detail},
            status_code=error.status_code
        )
    else:
        return templates.TemplateResponse(
            "pageError.html",
            context={"request": request,
                     "error": "422 Unprocessable Entity",
                     "detail": f"[{error.detail}]",  # [Possibly missing query string parameters]
                     "fix": f"{error.headers.get('fix')}"},  # Use the link that bot provided
            status_code=422
        )


@app.exception_handler(418)
async def im_a_teapot(request: Request, error: HTTPException):
    return templates.TemplateResponse(
        "pageError.html",
        context={"request": request,
                 "error": "418 I'm a teapot",
                 "detail": "[This server is a teapot, not a coffee machine]",
                 "fix": ""},
        status_code=418
    )


@app.exception_handler(404)
async def not_found(request: Request, error: HTTPException):
    if error.headers is None:
        error.headers = {}
    if request.headers.get("accept") == "application/json":
        return ORJSONResponse(
            {"code": error.status_code, "status": "error", "detail": error.detail, "fix": error.headers.get("fix")},
            status_code=error.status_code
        )
    else:
        return templates.TemplateResponse(
            "pageError.html",
            context={"request": request,
                     "error": "404 Not Found",
                     "detail": f"[{error.detail}]",  # [The page you are looking for does not exist]
                     "fix": f"{error.headers.get('fix')}"},
            status_code=404
        )


@app.exception_handler(403)
async def forbidden(request: Request, error: HTTPException) -> templates.TemplateResponse:
    if error.headers is None:
        error.headers = {}
    if request.headers.get("accept") == "application/json":
        return ORJSONResponse(
            {"code": error.status_code, "status": "error", "detail": error.detail, "fix": error.headers.get("fix")},
            status_code=error.status_code
        )
    else:
        return templates.TemplateResponse(
            "pageError.html",
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
    if request.headers.get("accept") == "application/json":
        return ORJSONResponse(
            {"code": error.status_code, "status": "error", "detail": error.detail, "fix": error.headers.get("fix")},
            status_code=error.status_code
        )
    else:
        return templates.TemplateResponse(
            "pageError.html",
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
    if request.headers.get("accept") == "application/json":
        return ORJSONResponse(
            {"code": error.status_code, "status": "error", "detail": error.detail, "fix": error.headers.get("fix")},
            status_code=error.status_code
        )
    else:
        return templates.TemplateResponse(
            "pageError.html",
            context={"request": request,
                     "error": "400 Bad Request",
                     "detail": f"[{error.detail}]",
                     "fix": f"{error.headers.get('fix')}"},
            status_code=400
        )
