#!/usr/bin/python3.10

class NothingFoundError(Exception):
    """
    Occurs when anything cannot by found in the database
    """

    def __init__(self):
        super().__init__(
            "The data you are looking for does not exist"
        )


class UnauthorizedError(Exception):
    """
    Occurs when anything cannot be obtained due to wrong credentials
    """

    def __init__(self):
        super().__init__(
            "The data you are looking cannot be obtained due to wrong credentials"
        )
