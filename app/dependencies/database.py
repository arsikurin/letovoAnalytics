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


@typing.final
class Postgresql:
    """
    Class for dealing with Postgresql
    """
    __slots__ = ("__connection",)
    counter = 0

    def __init__(self):
        self._connection: psycopg.AsyncConnection[typing.Any] = ...

    async def __aenter__(self) -> Postgresql:
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
    async def create() -> Postgresql:
        """
        Factory used for initializing database connection object

        Notes:
            Instead, use context manager, i.e. the `with` statement,
            because it allows you to forget about closing connections, etc.

        Returns:
            class instance with database connection
        """
        self = Postgresql()
        self._connection = await self._connect()
        return self

    @staticmethod
    async def _connect() -> psycopg.AsyncConnection[typing.Any]:
        """
        Connect to Postgres

        Returns:
            database connection
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
            log.exception(err)
            if self.counter == 0:
                self.counter += 1
                log.info(f"Trying to fix `{err}` Error!")
                await self._connection.close()
                self._connection = await self._connect()
                await self.get_users()

    async def get_analytics(self, sender_id: str) -> types_l.AnalyticsResponse:
        try:
            cursor = await self._connection.execute(
                "SELECT sender_id, schedule_counter, homework_counter, marks_counter, holidays_counter, clear_counter,"
                "options_counter, help_counter, about_counter, inline_counter FROM users WHERE sender_id = %s",
                (sender_id,)
            )
            cursor.row_factory = class_row(types_l.AnalyticsResponse)
            return await cursor.fetchone()
        except psycopg.OperationalError as err:
            log.exception(err)
            if self.counter == 0:
                self.counter += 1
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
            log.exception(err)
            if self.counter == 0:
                self.counter += 1
                log.info(f"Trying to fix `{err}` Error!")
                await self._connection.close()
                self._connection = await self._connect()
                await self.is_inited(sender_id)

    async def init_user(self, sender_id: str):
        try:
            await self._connection.execute(
                "INSERT INTO users ("
                "sender_id, schedule_counter, homework_counter, marks_counter, holidays_counter, "
                "clear_counter, options_counter, help_counter, about_counter, inline_counter"
                ") VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (sender_id, 0, 0, 0, 0, 0, 0, 0, 0, 0)
            )
            await self._connection.commit()
        except psycopg.OperationalError as err:
            log.exception(err)
            if self.counter == 0:
                self.counter += 1
                log.info(f"Trying to fix `{err}` Error!")
                await self._connection.close()
                self._connection = await self._connect()
                await self.init_user(sender_id)

    async def reset_analytics(self):
        try:
            # noinspection SqlWithoutWhere
            await self._connection.execute(
                "UPDATE users SET "
                "schedule_counter = %s, homework_counter = %s, marks_counter = %s, holidays_counter = %s, msg_ids = %s,"
                "clear_counter = %s, options_counter = %s, help_counter = %s, about_counter = %s, inline_counter = %s",
                (0, 0, 0, 0, "", 0, 0, 0, 0, 0)
            )
            await self._connection.commit()
        except psycopg.OperationalError as err:
            log.exception(err)
            if self.counter == 0:
                self.counter += 1
                log.info(f"Trying to fix `{err}` Error!")
                await self._connection.close()
                self._connection = await self._connect()
                await self.reset_analytics()

    async def set_msg_ids(self, sender_id: str, msg_ids: str):
        try:
            await self._connection.execute(
                "UPDATE users SET msg_ids = %s WHERE sender_id = %s",
                (msg_ids, sender_id)
            )
            await self._connection.commit()
        except psycopg.OperationalError as err:
            log.exception(err)
            if self.counter == 0:
                self.counter += 1
                log.info(f"Trying to fix `{err}` Error!")
                await self._connection.close()
                self._connection = await self._connect()
                await self.set_msg_ids(sender_id, msg_ids)

    async def get_msg_ids(self, sender_id: str) -> str:
        try:
            cursor = await self._connection.execute(
                "SELECT msg_ids FROM users WHERE sender_id = %s",
                (sender_id,)
            )
            return (await cursor.fetchone())[0]
        except psycopg.OperationalError as err:
            log.exception(err)
            if self.counter == 0:
                self.counter += 1
                log.info(f"Trying to fix `{err}` Error!")
                await self._connection.close()
                self._connection = await self._connect()
                await self.get_msg_ids(sender_id)

    async def increase_schedule_counter(self, sender_id: str):
        try:
            await self._connection.execute(
                "UPDATE users SET schedule_counter = schedule_counter + 1 WHERE sender_id = %s",
                (sender_id,)
            )
            await self._connection.commit()
        except psycopg.OperationalError as err:
            log.exception(err)
            if self.counter == 0:
                self.counter += 1
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
            log.exception(err)
            if self.counter == 0:
                self.counter += 1
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
            log.exception(err)
            if self.counter == 0:
                self.counter += 1
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
            log.exception(err)
            if self.counter == 0:
                self.counter += 1
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
            log.exception(err)
            if self.counter == 0:
                self.counter += 1
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
            log.exception(err)
            if self.counter == 0:
                self.counter += 1
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
            log.exception(err)
            if self.counter == 0:
                self.counter += 1
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
            log.exception(err)
            if err.__str__() == unknown_err:
                log.info(f"Trying to fix `{err}` Error!")
                await self._connection.close()
                self._connection = await self._connect()
                await self.increase_about_counter(sender_id)
