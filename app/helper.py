#!/usr/bin/python3.10

import essential
import asyncio
import requests as rq
import logging as log

from requests_futures.sessions import FuturesSession
from app.dependencies import Web, Database, Firebase, UnauthorizedError


async def main():
    log.debug("established connection to the Postgres")
    db = await Database.create()
    await db.reset_analytics()

    log.info("Updating tokens in Firebase")
    with FuturesSession() as session:
        for user in await Firebase.get_users():
            log.info(user)
            token = await Web.receive_token(s=session, sender_id=user)
            if token in (UnauthorizedError, rq.ConnectionError):
                continue
            await Firebase.update_data(sender_id=user, token=token)


if __name__ == "__main__":
    asyncio.run(main())
