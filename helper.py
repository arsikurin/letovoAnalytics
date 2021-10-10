#!/usr/bin/python3.10

import asyncio
import logging as log

from requests_futures.sessions import FuturesSession
from essential import (
    UnauthorizedError,
    Firebase,
    Web
)


async def main():
    log.info("Updating tokens in Firebase")
    with FuturesSession() as session:
        for user in await Firebase.get_users():
            token = await Web.receive_token(s=session, sender_id=user)
            if token == UnauthorizedError:
                continue
            await Firebase.update_data(sender_id=user, token=token)


if __name__ == "__main__":
    asyncio.run(main())
