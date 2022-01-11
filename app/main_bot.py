#!/usr/bin/python3.10
import aiohttp
import aiorun

import essential  # noqa
from app.bot import handlers, client
from app.dependencies import Postgresql, Firestore, run_sequence
from config import settings


async def main():
    async with aiohttp.ClientSession() as session, Postgresql() as db, Firestore() as fs, client:
        await run_sequence(
            handlers.include_handlers(session=session, db=db, fs=fs),
            client.start(bot_token=settings().TG_BOT_TOKEN),
            aiorun.shutdown_waits_for(client.run_until_disconnected())
        )


if __name__ == "__main__":
    aiorun.run(main(), use_uvloop=True)
