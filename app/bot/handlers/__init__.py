import asyncio
import datetime
import importlib
import inspect
import logging as log
import os
import time

import pyrogram
from pyrogram import Client, types

from app.bot import CallbackQuery, InlineQuery
from app.dependencies import Postgresql, Firestore, run_parallel, types as types_l


async def init(
        clients: types_l.clients[Client], cbQuery: CallbackQuery, iQuery: InlineQuery, db: Postgresql, fs: Firestore
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
        get_init_coro(handler, clients=clients, cbQuery=cbQuery, iQuery=iQuery, db=db, fs=fs, modules=modules)
        for handler in handlers
    )

    # Plugins may not have a valid init so those need to be filtered out
    await run_parallel(*(filter(None, to_init)))

    for client in clients:
        @client.on_message()
        async def _delete(_client: Client, message: types.Message):
            if _client.name == "letovoAnalytics":
                text = (
                    "**What you can do:**\n"
                    "\n"
                    "• Enter **/options** or click the **Options** button below\n"
                    "• Enter **/help** to view the manual"
                )
            else:
                text = (
                    "**This bot is used only for inline query**, i.e. `@l3tovobot [query]`\n"
                    "\n"
                    "Consider following @LetovoAnalyticsBot link"
                )

            await run_parallel(
                _client.send_message(
                    chat_id=message.from_user.id,
                    text=text,
                    reply_markup=types.ReplyKeyboardMarkup([
                        [
                            types.KeyboardButton("Options")
                        ]
                    ], resize_keyboard=True)
                ),
                message.delete()
            )
            raise pyrogram.StopPropagation


def get_init_coro(handler, /, **kwargs):
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
        log.info("Loaded handler %s (took %ds %dms)", handler.__name__, took.seconds, took.microseconds)
    except NotImplementedError:
        log.warning("Handler %s is not implemented. Skipping", handler.__name__)
    except Exception as err:
        log.exception("Failed to load handler %s", handler)
        print(err)  # Frankly, this statement is redundant. Placed here to avoid `too broad exception clause` warning


async def start_handlers(client, handlers):
    await asyncio.gather(*(_init_handler(client, handler) for handler in handlers))
