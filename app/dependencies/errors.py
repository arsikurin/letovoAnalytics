class NothingFoundError(Exception):
    """
    Occurs when anything cannot be found in the database
    """

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
    Occurs when anything cannot be obtained due to wrong credentials
    """

    def __init__(self, detail: str | None = None, fix: str | None = None):
        if detail is None:
            super().__init__(
                "The data you are looking cannot be obtained due to wrong credentials"
            )
        else:
            super().__init__(
                detail
            )
