#!/usr/bin/python3.10

import requests as rq
import logging as log

from essential import (
    MAIN_URL_API
)


def main():
    response = rq.get(MAIN_URL_API)
    log.debug(f"I am NOT sleeping {response.status_code}")


if __name__ == "__main__":
    main()
