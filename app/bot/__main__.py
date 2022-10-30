import asyncio
import contextlib
import logging as log

import aiohttp
import aiorun
from pyrogram import Client, compose

from app.bot import handlers, CallbackQuery, InlineQuery
from app.dependencies import Postgresql, Firestore, run_sequence, types as types_l
from config import settings


async def firestore_pinger(fs: Firestore):
    while True:
        log.debug("Sent ping to Firestore")
        await fs.is_logged("1")
        await asyncio.sleep(60 * 30)


async def main():
    client = Client(
        name="letovoAnalytics", api_id=settings().TG_API_ID, api_hash=settings().TG_API_HASH,
        bot_token=settings().TG_BOT_TOKEN, workers=settings().CONCURRENCY,
        test_mode=~settings().production + 2, in_memory=~settings().production + 2
    )
    client_i = Client(
        name="letovoAnalyticsInline", api_id=settings().TG_API_ID, api_hash=settings().TG_API_HASH,
        bot_token=settings().TG_BOT_TOKEN_INLINE, workers=settings().CONCURRENCY,
        test_mode=~settings().production + 2, in_memory=~settings().production + 2
    )

    async with aiohttp.ClientSession() as session, Postgresql() as db, Firestore() as fs:
        # noinspection PyPep8Naming
        cbQuery = CallbackQuery(client=client, session=session, db=db, fs=fs)
        # noinspection PyPep8Naming
        iQuery = InlineQuery(s=session)
        fs_pinger = asyncio.Task(firestore_pinger(fs))

        log.debug("Entered mainloop")
        await run_sequence(
            handlers.init(
                clients=types_l.Clients(client=client, client_i=client_i), cbQuery=cbQuery, iQuery=iQuery, db=db, fs=fs
            ),
            aiorun.shutdown_waits_for(compose([client, client_i]))
        )

        fs_pinger.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await fs_pinger


if __name__ == "__main__":
    asyncio.run(main())
    # aiorun.run(main(), use_uvloop=True, executor_workers=min(32, (os.cpu_count() or 1) + 4))
