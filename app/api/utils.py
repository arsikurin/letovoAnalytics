import functools as ft
import logging as log
from asyncio import iscoroutinefunction
from asyncio.coroutines import _is_coroutine  # noqa
from typing import Callable, TypeVar

from fastapi import FastAPI, Header, Request
from fastapi.dependencies.utils import solve_dependencies
from fastapi.exceptions import HTTPException
from fastapi.responses import ORJSONResponse
from fastapi.routing import get_dependant, run_endpoint_function

T = TypeVar("T")


async def get(app: FastAPI, func: Callable[..., T], request: Request = None) -> T:
    """
    Returns the result of calling `func` with its' dependencies, optionally with a request in scope
    """
    dependant = get_dependant(call=func, path='')
    request = request or Request(
        {'type': 'http', 'query_string': '', 'headers': [], 'app': app}
    )

    values, errors, *_ = await solve_dependencies(
        request=request, dependant=dependant, dependency_overrides_provider=app,
    )

    if errors:
        for err in errors:
            log.error(err)
        return ORJSONResponse({"code": 400, "status": "error", "detail": f"{errors}"}, status_code=400)

    return await run_endpoint_function(
        dependant=dependant, values=values, is_coroutine=iscoroutinefunction(func)
    )


class AcceptContent:
    __slots__ = ("routes", "_is_coroutine")

    def __init__(self):
        self.routes = {}
        self._is_coroutine = (
            _is_coroutine  # trick fastAPI into thinking this class is an async endpoint
        )

    async def __call__(self, request: Request, accept=Header(...)):  # noqa
        """as API endpoint"""
        for accept_content in accept.split(","):
            route = self.routes.get(accept_content, None)
            if route is not None:
                return await get(request.app, route, request)
        raise HTTPException(406)

    def accept_content_f(self, accept_content):

        @ft.wraps(accept_content)
        def wrapper(func):
            self.routes[accept_content] = func
            return self

        return wrapper


def accept(accept_content):
    """Use as decorator. Manages Accept header from requests"""
    return AcceptContent().accept_content_f(accept_content)
