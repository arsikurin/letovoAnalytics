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
    log.getLogger("telethon.network.mtprotosender").setLevel(log.INFO)
    log.getLogger("telethon.extensions.messagepacker").setLevel(log.INFO)
    log.getLogger("aiorun").setLevel(log.INFO)
    # log.getLogger("urllib3.connectionpool").disabled = True
    # log.getLogger("multipart.multipart").disabled = True

# fpath = os.path.join(os.path.dirname(__file__), 'utils')
# sys.path.append(fpath)

# start_time = time.perf_counter()
# datetime.timedelta(seconds=time.perf_counter() - start_time)
