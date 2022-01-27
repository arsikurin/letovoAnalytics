from __future__ import annotations

import itertools as it
import logging as log
import types
import typing

import psycopg
from psycopg.rows import class_row

from app.dependencies import types as types_l
from config import settings

unknown_err = "the connection is lost"


class AnalyticsDatabase(typing.Protocol):
    """
    Class for dealing with relational DB
    """
    __slots__ = ("__connection",)

    async def __aenter__(self) -> AnalyticsDatabase: ...

    async def __aexit__(
            self,
            exc_type: typing.Type[BaseException] | None,
            exc_val: BaseException | None,
            exc_tb: types.TracebackType | None,
    ): ...

    @property
    def _connection(self) -> psycopg.AsyncConnection[typing.Any]: ...

    @staticmethod
    async def create() -> AnalyticsDatabase:
        """
        Factory
        """

    @staticmethod
    async def _connect() -> psycopg.AsyncConnection[typing.Any]: ...

    async def disconnect(self): ...

    async def get_users(self) -> typing.Iterator[str]: ...

    async def get_analytics(self, sender_id: str) -> types_l.AnalyticsResponse: ...

    async def is_inited(self, sender_id: str) -> bool: ...

    async def init_user(self, sender_id: str): ...

    async def reset_analytics(self): ...

    async def increase_schedule_counter(self, sender_id: str): ...

    async def increase_homework_counter(self, sender_id: str): ...

    async def increase_marks_counter(self, sender_id: str): ...

    async def increase_holidays_counter(self, sender_id: str): ...

    async def increase_options_counter(self, sender_id: str): ...

    async def increase_help_counter(self, sender_id: str): ...

    async def increase_inline_counter(self, sender_id: str): ...

    async def increase_about_counter(self, sender_id: str): ...


@typing.final
class Postgresql:
    """
    Class for working with relational DB
    """
    __slots__ = ("__connection",)

    def __init__(self):
        self._connection: psycopg.AsyncConnection[typing.Any] = ...

    async def __aenter__(self) -> AnalyticsDatabase:
        self._connection = await self._connect()
        return self

    async def __aexit__(
            self,
            exc_type: typing.Type[BaseException] | None,
            exc_val: BaseException | None,
            exc_tb: types.TracebackType | None,
    ):
        await self._connection.__aexit__(exc_type=exc_type, exc_val=exc_val, exc_tb=exc_tb)

    @property
    def _connection(self) -> psycopg.AsyncConnection[typing.Any]:
        return self.__connection

    @_connection.setter
    def _connection(self, value: psycopg.AsyncConnection[typing.Any]):
        self.__connection = value

    @staticmethod
    async def create() -> AnalyticsDatabase:
        """
        Factory
        """
        self_ = Postgresql()
        self_._connection = await self_._connect()
        return self_

    @staticmethod
    async def _connect() -> psycopg.AsyncConnection[typing.Any]:
        """
        Connect to Postgres
        """
        return await psycopg.AsyncConnection.connect(
            conninfo=settings().DATABASE_URL, sslmode="require"  # , row_factory=class_row(`class`)
        )

    async def disconnect(self):
        await self._connection.close()

    async def get_users(self) -> typing.Iterator[str]:
        try:
            cursor = await self._connection.execute(
                "SELECT sender_id FROM users"
            )
            return it.chain.from_iterable(await cursor.fetchall())
        except psycopg.OperationalError as err:
            log.error(err)
            if err == unknown_err:
                log.info(f"Trying to fix `{err}` Error!")
                await self._connection.close()
                self._connection = await self._connect()
                await self.get_users()

    async def get_analytics(self, sender_id: str) -> types_l.AnalyticsResponse:
        # TODO refactor wildcard
        try:
            cursor = await self._connection.execute(
                "SELECT * FROM users WHERE sender_id = %s",
                (sender_id,)
            )
            cursor.row_factory = class_row(types_l.AnalyticsResponse)
            return await cursor.fetchone()
        except psycopg.OperationalError as err:
            log.error(err)
            if err == unknown_err:
                log.info(f"Trying to fix `{err}` Error!")
                await self._connection.close()
                self._connection = await self._connect()
                await self.get_analytics(sender_id)

    async def is_inited(self, sender_id: str) -> bool:
        try:
            cursor = await self._connection.execute(
                "SELECT sender_id FROM users WHERE sender_id = %s",
                (sender_id,)
            )
            return bool(await cursor.fetchone())
        except psycopg.OperationalError as err:
            log.error(err)
            if err == unknown_err:
                log.info(f"Trying to fix `{err}` Error!")
                await self._connection.close()
                self._connection = await self._connect()
                await self.is_inited(sender_id)

    async def init_user(self, sender_id: str):
        try:
            await self._connection.execute(
                "INSERT INTO users ("
                "sender_id, message_id, schedule_counter, homework_counter, marks_counter, holidays_counter, "
                "clear_counter, options_counter, help_counter, about_counter, inline_counter"
                ") VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (sender_id, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
            )
            await self._connection.commit()
        except psycopg.OperationalError as err:
            log.error(err)
            if err == unknown_err:
                log.info(f"Trying to fix `{err}` Error!")
                await self._connection.close()
                self._connection = await self._connect()
                await self.init_user(sender_id)

    async def reset_analytics(self):
        try:
            await self._connection.execute(
                "UPDATE users SET "  # noqa
                "schedule_counter = %s, homework_counter = %s, marks_counter = %s, holidays_counter = %s, "
                "clear_counter = %s, options_counter = %s, help_counter = %s, about_counter = %s, inline_counter = %s",
                (0, 0, 0, 0, 0, 0, 0, 0, 0)
            )
            await self._connection.commit()
        except psycopg.OperationalError as err:
            log.error(err)
            if err == unknown_err:
                log.info(f"Trying to fix `{err}` Error!")
                await self._connection.close()
                self._connection = await self._connect()
                await self.reset_analytics()

    async def increase_schedule_counter(self, sender_id: str):
        try:
            await self._connection.execute(
                "UPDATE users SET schedule_counter = schedule_counter + 1 WHERE sender_id = %s",
                (sender_id,)
            )
            await self._connection.commit()
        except psycopg.OperationalError as err:
            log.error(err)
            if err == unknown_err:
                log.info(f"Trying to fix `{err}` Error!")
                await self._connection.close()
                self._connection = await self._connect()
                await self.increase_schedule_counter(sender_id)

    async def increase_homework_counter(self, sender_id: str):
        try:
            await self._connection.execute(
                "UPDATE users SET homework_counter = homework_counter + 1 WHERE sender_id = %s",
                (sender_id,)
            )
            await self._connection.commit()
        except psycopg.OperationalError as err:
            log.error(err)
            if err == unknown_err:
                log.info(f"Trying to fix `{err}` Error!")
                await self._connection.close()
                self._connection = await self._connect()
                await self.increase_homework_counter(sender_id)

    async def increase_marks_counter(self, sender_id: str):
        try:
            await self._connection.execute(
                "UPDATE users SET marks_counter = marks_counter + 1 WHERE sender_id = %s",
                (sender_id,)
            )
            await self._connection.commit()
        except psycopg.OperationalError as err:
            log.error(err)
            if err == unknown_err:
                log.info(f"Trying to fix `{err}` Error!")
                await self._connection.close()
                self._connection = await self._connect()
                await self.increase_marks_counter(sender_id)

    async def increase_holidays_counter(self, sender_id: str):
        try:
            await self._connection.execute(
                "UPDATE users SET holidays_counter = holidays_counter + 1 WHERE sender_id = %s",
                (sender_id,)
            )
            await self._connection.commit()
        except psycopg.OperationalError as err:
            log.error(err)
            if err == unknown_err:
                log.info(f"Trying to fix `{err}` Error!")
                await self._connection.close()
                self._connection = await self._connect()
                await self.increase_holidays_counter(sender_id)

    async def increase_options_counter(self, sender_id: str):
        try:
            await self._connection.execute(
                "UPDATE users SET options_counter = options_counter + 1 WHERE sender_id= %s",
                (sender_id,)
            )
            await self._connection.commit()
        except psycopg.OperationalError as err:
            log.error(err)
            if err == unknown_err:
                log.info(f"Trying to fix `{err}` Error!")
                await self._connection.close()
                self._connection = await self._connect()
                await self.increase_options_counter(sender_id)

    async def increase_help_counter(self, sender_id: str):
        try:
            await self._connection.execute(
                "UPDATE users SET help_counter = help_counter + 1 WHERE sender_id = %s",
                (sender_id,)
            )
            await self._connection.commit()
        except psycopg.OperationalError as err:
            log.error(err)
            if err == unknown_err:
                log.info(f"Trying to fix `{err}` Error!")
                await self._connection.close()
                self._connection = await self._connect()
                await self.increase_help_counter(sender_id)

    async def increase_inline_counter(self, sender_id: str):
        try:
            await self._connection.execute(
                "UPDATE users SET inline_counter = inline_counter + 1 WHERE sender_id = %s",
                (sender_id,)
            )
            await self._connection.commit()
        except psycopg.OperationalError as err:
            log.error(err)
            if err == unknown_err:
                log.info(f"Trying to fix `{err}` Error!")
                await self._connection.close()
                self._connection = await self._connect()
                await self.increase_inline_counter(sender_id)

    async def increase_about_counter(self, sender_id: str):
        try:
            await self._connection.execute(
                "UPDATE users SET about_counter = inline_counter + 1 WHERE sender_id = %s",
                (sender_id,)
            )
            await self._connection.commit()
        except psycopg.OperationalError as err:
            log.error(err)
            if err.__str__() == unknown_err:
                log.info(f"Trying to fix `{err}` Error!")
                await self._connection.close()
                self._connection = await self._connect()
                await self.increase_about_counter(sender_id)
