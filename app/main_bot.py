import asyncio
import logging as log
import os

import aiohttp
import aiorun
from pyrogram import Client

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
    client = Client(
        name="letovoAnalytics", api_id=settings().TG_API_ID, api_hash=settings().TG_API_HASH,
        bot_token=settings().TG_BOT_TOKEN, workers=min(32, (os.cpu_count() or 1) + 4), test_mode=False, in_memory=False
    )

    async with client, aiohttp.ClientSession() as session, Postgresql() as db, Firestore() as fs:
        cbQuery = CallbackQuery(client=client, session=session, db=db, fs=fs)
        iQuery = InlineQuery(s=session)

        log.debug("Entered mainloop")
        await run_parallel(
            firestore_pinger(fs),
            run_sequence(
                handlers.init(client=client, cbQuery=cbQuery, iQuery=iQuery, db=db, fs=fs),
                # aiorun.shutdown_waits_for(client.run())
            )
        )


if __name__ == "__main__":
    aiorun.run(main(), use_uvloop=True, executor_workers=min(32, (os.cpu_count() or 1) + 4))
