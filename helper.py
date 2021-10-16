#!/usr/bin/python3.10

import customization
import asyncio
import requests as rq
import logging as log

from requests_futures.sessions import FuturesSession
from classes.errors import UnauthorizedError
from classes.firebase import Firebase
from classes.web import Web


async def main():
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
