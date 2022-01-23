#!/usr/bin/python3.10

import asyncio
import logging as log

import aiohttp

import essential  # noqa
from config import settings


async def main() -> bytes:
    async with aiohttp.ClientSession() as session:
        async with session.get(url=settings().URL_MAIN_API) as resp:
            if resp.status != 200:
                log.info(f"Something went wrong. {resp.status}")
            else:
                log.info("Sent ping to the API")
            return await resp.content.read()


if __name__ == "__main__":
    asyncio.run(main())
