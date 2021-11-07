#!/usr/bin/python3.10

import essential
import aiorun
import aiohttp

from config import settings
from app.bot import handlers, client

session: aiohttp.ClientSession = ...


async def main():
    global session
    session = aiohttp.ClientSession()

    await handlers.include_handlers(session)
    await client.start(bot_token=settings().TG_BOT_TOKEN)
    await client.run_until_disconnected()


async def on_shutdown():
    await session.close()


if __name__ == "__main__":
    aiorun.run(main(), use_uvloop=True, shutdown_callback=on_shutdown())
