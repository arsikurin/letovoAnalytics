#!/usr/bin/python3.10

import asyncio
import logging as log

import aiohttp

import essential  # noqa
from app.dependencies import Web, Database, Firebase, UnauthorizedError, NothingFoundError


async def main():
    log.debug("established connection to the Postgres")
    db = await Database.create()
    await db.reset_analytics()

    log.info("Updating tokens in Firebase")
    async with aiohttp.ClientSession() as session:
        web = Web(session)
        async for user in await Firebase.get_users():
            log.info(user.id)
            try:
                token = await web.receive_token(sender_id=user.id)
            except (NothingFoundError, UnauthorizedError, aiohttp.ClientConnectionError):
                continue

            await Firebase.update_data(sender_id=user.id, token=token)


if __name__ == "__main__":
    asyncio.run(main())