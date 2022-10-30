import asyncio
import logging as log
import os
import sys

import uvloop
from colourlib import Fg, Style

"""
add root folder of the project to the PYTHONPATH
in order to access files using absolute paths

for example:
`import root.module.submodule`
"""
PROJECT_ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        os.pardir
    )
)
sys.path.append(PROJECT_ROOT)
from config import settings  # noqa

# set asyncio policy to use uvloop as event loop
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

# initialize logger
log.basicConfig(
    format=f"{Style.Bold}(%(levelname)s) {Fg.Green}%(asctime)s{Fg.Reset} {Style.Bold}%(message)s{Style.Reset}"
           f"\n[%(name)s] — (%(filename)s).%(funcName)s(%(lineno)d)\n",
    level=log.DEBUG, stream=sys.stdout
)
log.getLogger("pyrogram.session.session").setLevel(log.INFO)
log.getLogger("aiorun").setLevel(log.INFO)

# fpath = os.path.join(os.path.dirname(__file__), 'utils')
# sys.path.append(fpath)

# start_time = time.perf_counter()
# datetime.timedelta(seconds=time.perf_counter() - start_time)

match sys.argv[-1].lower():
    case "bot":
        from app.bot.__main__ import main

        asyncio.run(main())

    case "api":
        import uvicorn
        from app.api.__main__ import app

        c = uvicorn.Config(
            app=app, host="0.0.0.0", port=settings().PORT, workers=settings().CONCURRENCY, http="httptools",
            loop="uvloop"
        )  # limit_concurrency

        uvicorn.Server(config=c).run()

    case "update":
        # noinspection PyUnresolvedReferences
        import aiohttp
        from app.dependencies import API, Postgresql, Firestore, run_immediately, run_parallel


        @run_immediately
        async def _():
            log.info("Updating tokens in the Firebase")
            async with aiohttp.ClientSession() as session, Postgresql() as db, Firestore(app_name="helper") as fs:
                log.debug("established connections to the databases")

                api = API(session=session, fs=fs)
                await run_parallel(
                    fs.update_tokens(api),
                    db.reset_analytics()
                )
                log.debug("done reset analytics")

    case "ping":
        import aiohttp
        from app.dependencies import run_immediately


        @run_immediately
        async def _() -> bytes:
            async with aiohttp.ClientSession() as session:
                async with session.get(url=settings().URL_MAIN_API) as resp:
                    if resp.status != 200:
                        log.info(f"Something went wrong. {resp.status}")
                    else:
                        log.info("Sent ping to the API")

                    return await resp.content.read()

    case _:
        print("ERROR: Neither `bot` nor `api` nor `update` nor `ping` provided")
