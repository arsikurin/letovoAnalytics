#!/usr/bin/python3.10

import asyncio
import logging as log

import aiohttp
import requests as rq
from requests_futures.sessions import FuturesSession

import essential  # noqa
from app.dependencies import Web, Database, Firebase, UnauthorizedError, NothingFoundError


async def main():
    log.debug("established connection to the Postgres")
    db = await Database.create()
    await db.reset_analytics()

    log.info("Updating tokens in Firebase")
    with FuturesSession() as session:  # TODO
        for user in await Firebase.get_users():
            log.info(user)
            try:
                token = await Web.receive_token(session=session, sender_id=user)
            except (NothingFoundError, UnauthorizedError, aiohttp.ClientConnectionError):
                continue

            await Firebase.update_data(sender_id=user, token=token)


if __name__ == "__main__":
    asyncio.run(main())
