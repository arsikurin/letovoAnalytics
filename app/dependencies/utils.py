import asyncio
import typing


def run_immediately(function: typing.Callable):
    """
    Decorator used to execute asynchronous functions more conveniently
    """
    asyncio.run(function())


async def run_sequence_ag(*functions: typing.Awaitable[typing.Any]) -> typing.AsyncGenerator:
    """
    Run provided functions in sequence. Yields values from functions
    """
    for func in functions:
        yield await func


async def run_sequence(*functions: typing.Awaitable[typing.Any]):
    """
    Run provided functions in sequence
    """
    for func in functions:
        await func


async def run_parallel(*functions: typing.Awaitable[typing.Any]) -> tuple:
    """
    Run provided functions in parallel
    """
    return await asyncio.gather(*functions)
