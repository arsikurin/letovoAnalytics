#!/usr/bin/python3.10
import aiohttp
import aiorun

import essential  # noqa
from app.bot import handlers, client
from app.dependencies import Postgresql, Firestore, AnalyticsDatabase, CredentialsDatabase, run_parallel
from config import settings

session: aiohttp.ClientSession = ...
db: AnalyticsDatabase = ...
fs: CredentialsDatabase = ...


async def main():
    global session, db, fs
    session = aiohttp.ClientSession()
    db = await Postgresql.create()
    fs = await Firestore.create()

    await handlers.include_handlers(session=session, db=db, fs=fs)
    await client.start(bot_token=settings().TG_BOT_TOKEN)
    await client.run_until_disconnected()


async def on_shutdown():
    await run_parallel(
        session.close(),
        db.disconnect(),
        fs.disconnect()
    )


if __name__ == "__main__":
    aiorun.run(main(), use_uvloop=True, shutdown_callback=on_shutdown())
