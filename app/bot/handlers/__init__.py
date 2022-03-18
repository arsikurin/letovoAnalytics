import asyncio
import datetime
import importlib
import inspect
import logging as log
import os
import time

from telethon import TelegramClient, events, types

from app.bot import CallbackQuery, InlineQuery
from app.dependencies import Postgresql, Firestore, run_parallel


async def init(
        client: TelegramClient, cbQuery: CallbackQuery, iQuery: InlineQuery, db: Postgresql, fs: Firestore
):
    handlers = [
        # Dynamically import
        importlib.import_module(".", f"{__name__}.{file[:-3]}")

        # All the files in the current directory
        for file in sorted(os.listdir(os.path.dirname(__file__)), key=lambda x: x[-4])

        # If they start with a letter and are Python files
        if file[0].isalpha() and file.endswith(".py")
    ]

    # Keep a mapping of module name to module for easy access inside the handlers
    modules = {m.__name__.split(".")[-1]: m for m in handlers}

    # All kwargs provided to get_init_args are those that handlers may access
    to_init = (
        get_init_coro(handler, client=client, cbQuery=cbQuery, iQuery=iQuery, db=db, fs=fs, modules=modules)
        for handler in handlers
    )

    # Plugins may not have a valid init so those need to be filtered out
    await run_parallel(*(filter(None, to_init)))

    @client.on(events.NewMessage())
    async def _delete(event: events.NewMessage.Event):
        sender: types.User = await event.get_sender()
        message, _, = await run_parallel(
            cbQuery.send_common_page(sender=sender),
            event.delete()
        )
        raise events.StopPropagation


def get_init_coro(handler, **kwargs):
    p_init = getattr(handler, "init", None)
    if not callable(p_init):
        return

    result_kwargs = {}
    sig = inspect.signature(p_init)
    for param in sig.parameters:
        if param in kwargs:
            result_kwargs[param] = kwargs[param]
        else:
            log.error("Handler %s has unknown init parameter %s", handler.__name__, param)
            return

    return _init_handler(handler, result_kwargs)


async def _init_handler(handler, kwargs):
    try:
        # log.debug(f"Loading handler {handler.__name__}…")
        start_time = time.perf_counter()
        await handler.init(**kwargs)
        took = datetime.timedelta(seconds=time.perf_counter() - start_time)
        log.info(f"Loaded handler {handler.__name__} (took {took.seconds}s {took.microseconds}ms)")
    except NotImplementedError:
        log.warning(f"Handler {handler.__name__} is not implemented. Skipping")
    except Exception as err:
        log.exception(f"Failed to load handler {handler}")
        print(err)  # Frankly, this statement is redundant. Placed here to avoid `too broad exception clause` warning


async def start_handlers(client, handlers):
    await asyncio.gather(*(_init_handler(client, handler) for handler in handlers))
