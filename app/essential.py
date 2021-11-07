import os
import sys
import asyncio
import uvloop
import logging as log

from colourlib import Fg, Style

VERBOSE = True
PROJECT_ROOT = os.path.abspath(os.path.join(
    os.path.dirname(__file__),
    os.pardir)
)
sys.path.append(PROJECT_ROOT)
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

# start_time = time.perf_counter()
# datetime.timedelta(seconds=time.perf_counter() - start_time)


if VERBOSE:
    log.basicConfig(
        format=f"{Style.Bold}(%(levelname)s) {Fg.Green}%(asctime)s{Fg.Reset} {Style.Bold}%(message)s{Style.Reset}"
               f"\n[%(name)s]\n",
        level=log.DEBUG
    )
else:
    log.basicConfig(
        format=f"{Style.Bold}(%(levelname)s) {Fg.Green}%(asctime)s{Fg.Reset} {Style.Bold}%(message)s{Style.Reset}"
               f"\n[%(name)s]\n",
        level=log.INFO
    )
