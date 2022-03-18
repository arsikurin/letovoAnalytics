#!/usr/bin/env python3
import asyncio
import logging as log

import aiohttp
import aiorun
from telethon import TelegramClient

import essential  # noqa: used to initialize PYTHONPATH and logger
from app.bot import handlers, CallbackQuery, InlineQuery
from app.dependencies import Postgresql, Firestore, run_sequence, run_parallel
from config import settings


async def firestore_pinger(fs: Firestore):
    while True:
        log.debug("Sent ping to Firestore")
        await fs.is_logged("1")
        await asyncio.sleep(60 * 30)


async def main():
    client = await TelegramClient(  # noqa: `TelegramClient.start(...)` returns a coro
        session="letovoAnalytics", api_id=settings().TG_API_ID, api_hash=settings().TG_API_HASH
    ).start(bot_token=settings().TG_BOT_TOKEN)

    async with aiohttp.ClientSession() as session, Postgresql() as db, Firestore() as fs, client:
        cbQuery = CallbackQuery(client=client, session=session, db=db, fs=fs)
        iQuery = InlineQuery(s=session)

        log.debug("Entered mainloop")
        await run_parallel(
            firestore_pinger(fs),
            run_sequence(
                handlers.init(client=client, cbQuery=cbQuery, iQuery=iQuery, db=db, fs=fs),
                aiorun.shutdown_waits_for(client.run_until_disconnected())
            )
        )


if __name__ == "__main__":
    aiorun.run(main(), use_uvloop=True, executor_workers=20)
