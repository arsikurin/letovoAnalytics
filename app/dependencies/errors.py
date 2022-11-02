class NothingFoundError(Exception):
    """
    Occurs when anything cannot be found in the database
    """

    __notes__ = "Consider entering /start and registering afterwards"

    def __init__(self, detail: str | None = None):
        if detail is None:
            super().__init__(
                "The data you are looking for does not exist"
            )
        else:
            super().__init__(
                detail
            )


class UnauthorizedError(Exception):
    """
    Occurs when anything cannot be obtained due to the wrong credentials
    """

    def __init__(self, detail: str | None = None, fix: str | None = None):
        if detail is None:
            super().__init__(
                "The data you are looking cannot be obtained due to the wrong credentials"
            )
        else:
            super().__init__(
                detail
            )


class StopPropagation(Exception):
    """
    Occurs when it is required to stop the execution.
    It can be seen as the ``StopIteration`` in a for loop
    """

    def __init__(self, detail: str | None = None, fix: str | None = None):
        if detail is None:
            super().__init__(
                "Stop execution"
            )
        else:
            super().__init__(
                detail
            )


class TooManyRequests(Exception):
    """
    Occurs when got 429 http code
    """

    def __init__(self, detail: str | None = None, fix: str | None = None):
        if detail is None:
            super().__init__(
                "Too many requests"
            )
        else:
            super().__init__(
                detail
            )
