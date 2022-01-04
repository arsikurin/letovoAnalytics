#!/usr/bin/python3.10

import asyncio
import logging as log

import aiohttp

import essential  # noqa
from app.dependencies import Web, Postgresql, Firestore, UnauthorizedError, NothingFoundError


async def main():
    log.debug("established connection to the Postgres")
    db = await Postgresql.create()
    fs = Firestore.create()
    await db.reset_analytics()

    log.info("Updating tokens in Firebase")
    async with aiohttp.ClientSession() as session:
        web = Web(session)
        async for user in await fs.get_users():
            try:
                token = await web.receive_token(sender_id=user.id, fs=fs)
            except (NothingFoundError, UnauthorizedError, aiohttp.ClientConnectionError):
                log.info(f"Skipped {user.id}")
                continue

            await fs.update_data(sender_id=user.id, token=token)
            log.info(f"Updated {user.id}")


if __name__ == "__main__":
    asyncio.run(main())
