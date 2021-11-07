import asyncio


def execute_immediately(func):
    """
    Decorator used to execute asynchronous functions more conveniently
    """
    asyncio.run(func())
