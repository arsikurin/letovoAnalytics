import asyncio
import logging as log
import os
import sys

import uvloop
from colourlib import Fg, Style

PROJECT_ROOT = os.path.abspath(os.path.join(
    os.path.dirname(__file__),
    os.pardir)
)
sys.path.append(PROJECT_ROOT)

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
from config import settings  # noqa

# start_time = time.perf_counter()
# datetime.timedelta(seconds=time.perf_counter() - start_time)


if settings().debug:
    log.basicConfig(
        format=f"{Style.Bold}(%(levelname)s) {Fg.Green}%(asctime)s{Fg.Reset} {Style.Bold}%(message)s{Style.Reset}"
               f"\n[%(name)s]\n",
        level=log.DEBUG
    )

else:
    log.basicConfig(
        format=f"{Style.Bold}(%(levelname)s) {Fg.Green}%(asctime)s{Fg.Reset} {Style.Bold}%(message)s{Style.Reset}"
               f"\n[%(name)s]\n",
        level=log.DEBUG
    )
    log.getLogger("telethon.network.mtprotosender").level = log.INFO
    log.getLogger("telethon.extensions.messagepacker").level = log.INFO
    # log.getLogger("urllib3.connectionpool").disabled = True
    # log.getLogger("multipart.multipart").disabled = True
