#!/usr/bin/python3.10

import customization
import requests as rq
import logging as log

from constants import MAIN_URL_API


def main():
    response = rq.get(MAIN_URL_API)
    log.info(f"I am NOT sleeping {response.status_code}")


if __name__ == "__main__":
    main()
