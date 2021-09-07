import asyncio
import logging as log

from requests_futures.sessions import FuturesSession
from essential import (
    Firebase,
    Web
)


async def main():
    log.debug("Working")
    with FuturesSession() as session:
        for user in await Firebase.get_users():
            await Firebase.update_data(sender_id=user, token=await Web.receive_token(s=session, sender_id=user))


if __name__ == "__main__":
    asyncio.run(main())
