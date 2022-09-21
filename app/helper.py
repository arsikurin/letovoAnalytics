import asyncio
import logging as log

import aiohttp

# noinspection PyUnresolvedReferences
import essential
from app.dependencies import API, Postgresql, Firestore, errors as errors_l


async def main():
    log.info("Updating tokens in Firebase")
    async with aiohttp.ClientSession() as session, Postgresql() as db, Firestore(app_name="helper") as fs:
        log.debug("established connections to the databases")
        web = API(session=session, fs=fs)
        if __name__ == "__main__":
            await db.reset_analytics()
            log.debug("done reset analytics")

        async for user in await fs.get_users():
            try:
                token = await web.receive_token(sender_id=user.id)
            except (errors_l.NothingFoundError, errors_l.UnauthorizedError, aiohttp.ClientConnectionError) as err:
                log.info(f"Skipped {user.id} {err}")
                continue

            await fs.update_data(sender_id=user.id, token=token)
            log.info(f"Updated {user.id}")


if __name__ == "__main__":
    asyncio.run(main())
