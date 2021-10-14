#!/usr/bin/python3.10

import custom_logging
import asyncio
import logging as log

from requests_futures.sessions import FuturesSession
from classes.errors import UnauthorizedError
from classes.firebase import Firebase
from classes.web import Web


async def main():
    log.info("Updating tokens in Firebase")
    with FuturesSession() as session:
        for user in await Firebase.get_users():
            token = await Web.receive_token(s=session, sender_id=user)
            if token == UnauthorizedError:
                continue
            await Firebase.update_data(sender_id=user, token=token)
            await Firebase.update_analytics(
                sender_id=user, schedule_entire=0, schedule_today=0, schedule_specific=0,
                homework_entire=0, homework_tomorrow=0, homework_specific=0, marks_all=0,
                marks_summative=0, marks_recent=0, holidays=0, clear_previous=0, options=0,
                help=0, start=0, about=0, inline=0
            )


if __name__ == "__main__":
    asyncio.run(main())
