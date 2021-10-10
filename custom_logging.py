#!/usr/bin/python3.10

import logging as log
from colourlib import Fg, Style

VERBOSE = True
# start_time = time.perf_counter()
# datetime.timedelta(seconds=time.perf_counter() - start_time)

if VERBOSE:
    log.basicConfig(
        format=f"{Fg.Green}{Style.Bold}%(asctime)s{Fg.Reset}{Style.Bold} %(message)s{Style.Reset}\n[%(name)s]\n",
        level=log.DEBUG
    )
else:
    try:
        from debug import *
    except ImportError:
        pass
    log.basicConfig(
        format=f"{Fg.Green}{Style.Bold}%(asctime)s{Fg.Reset}{Style.Bold} %(message)s{Style.Reset}\n[%(name)s]\n",
        level=log.INFO
    )



