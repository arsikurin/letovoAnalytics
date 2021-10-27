#!/usr/bin/python3.10

import asyncio
import uvloop
import logging as log

from colourlib import Fg, Style

VERBOSE = True
asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


def execute_immediately(func):
    """
    Decorator used to execute asynchronous functions more conveniently
    """
    asyncio.run(func())


# start_time = time.perf_counter()
# datetime.timedelta(seconds=time.perf_counter() - start_time)
try:
    from debug import *

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
except ImportError:
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
