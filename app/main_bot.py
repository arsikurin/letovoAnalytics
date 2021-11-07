#!/usr/bin/python3.10

import essential
import aiorun

from config import settings
from app.bot import handlers, client


async def main():
    await client.start(bot_token=settings().TG_BOT_TOKEN)
    await client.run_until_disconnected()


if __name__ == "__main__":
    aiorun.run(main(), use_uvloop=True)
