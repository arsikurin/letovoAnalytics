from __future__ import annotations

import logging as log

import psycopg

from config import settings


class Database:
    """
    Class for working with relational DB
    """
    __slots__ = ("_connection",)

    def __init__(self):
        self.connection: psycopg.AsyncConnection = ...

    @staticmethod
    async def create() -> Database:
        self = Database()
        self.connection = await Database._connect()
        # self.connection = await psycopg.AsyncConnection.connect(
        #     host=HOST_SQL, user=USER_SQL, dbname=DATABASE_SQL, password=PASSWORD_SQL, sslmode="require"
        # )
        return self

    @staticmethod
    async def _connect() -> psycopg.AsyncConnection:
        return await psycopg.AsyncConnection.connect(
            host=settings().SQL_HOST, user=settings().SQL_USER, dbname=settings().SQL_DBNAME,
            password=settings().SQL_PASSWORD, sslmode="require"
        )

    async def get_users(self) -> list:
        try:
            cursor = await self.connection.execute(
                "SELECT sender_id FROM users"
            )
            return await cursor.fetchall()
        except psycopg.OperationalError as err:
            log.error(err)
            if err == "the connection is lost":
                self.connection = await self._connect()
                await self.get_users()

    async def get_analytics(self, sender_id: str) -> list:
        try:
            cursor = await self.connection.execute(
                "SELECT * FROM users WHERE sender_id = %s",
                (sender_id,)
            )
            return await cursor.fetchone()
        except psycopg.OperationalError as err:
            log.error(err)
            if err == "the connection is lost":
                self.connection = await self._connect()
                await self.get_analytics(sender_id)

    async def is_inited(self, sender_id: str) -> str:
        try:
            cursor = await self.connection.execute(
                "SELECT sender_id FROM users WHERE sender_id = %s",
                (sender_id,)
            )
            return await cursor.fetchone()
        except psycopg.OperationalError as err:
            log.error(err)
            if err == "the connection is lost":
                self.connection = await self._connect()
                await self.is_inited(sender_id)

    async def init_user(self, sender_id: str):
        try:
            await self.connection.execute(
                "INSERT INTO users ("
                "sender_id, message_id, schedule_counter, homework_counter, marks_counter, holidays_counter, "
                "clear_counter, options_counter, help_counter, about_counter, inline_counter"
                ") VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (sender_id, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
            )
            await self.connection.commit()
        except psycopg.OperationalError as err:
            log.error(err)
            if err == "the connection is lost":
                self.connection = await Database._connect()
                await self.init_user(sender_id)

    async def reset_analytics(self):
        try:
            await self.connection.execute(
                "UPDATE users SET "
                "schedule_counter = %s, homework_counter = %s, marks_counter = %s, holidays_counter = %s, "
                "clear_counter = %s, options_counter = %s, help_counter = %s, about_counter = %s, inline_counter = %s",
                (0, 0, 0, 0, 0, 0, 0, 0, 0)
            )
            await self.connection.commit()
        except psycopg.OperationalError as err:
            log.error(err)
            if err == "the connection is lost":
                self.connection = await Database._connect()
                await self.reset_analytics()

    async def get_schedule_counter(self, sender_id: str) -> int:
        cursor = await self.connection.execute(
            "SELECT schedule_counter FROM users WHERE sender_id = %s",
            (sender_id,)
        )
        return (await cursor.fetchone())[0]

    async def get_homework_counter(self, sender_id: str) -> int:
        cursor = await self.connection.execute(
            "SELECT homework_counter FROM users WHERE sender_id = %s",
            (sender_id,)
        )
        return (await cursor.fetchone())[0]

    async def get_marks_counter(self, sender_id: str) -> int:
        cursor = await self.connection.execute(
            "SELECT marks_counter FROM users WHERE sender_id = %s",
            (sender_id,)
        )
        return (await cursor.fetchone())[0]

    async def get_holidays_counter(self, sender_id: str) -> int:
        cursor = await self.connection.execute(
            "SELECT holidays_counter FROM users WHERE sender_id = %s",
            (sender_id,)
        )
        return (await cursor.fetchone())[0]

    async def get_options_counter(self, sender_id: str) -> int:
        cursor = await self.connection.execute(
            "SELECT options_counter FROM users WHERE sender_id = %s",
            (sender_id,)
        )
        return (await cursor.fetchone())[0]

    async def get_help_counter(self, sender_id: str) -> int:
        cursor = await self.connection.execute(
            "SELECT help_counter FROM users WHERE sender_id = %s",
            (sender_id,)
        )
        return (await cursor.fetchone())[0]

    async def get_inline_counter(self, sender_id: str) -> int:
        cursor = await self.connection.execute(
            "SELECT inline_counter FROM users WHERE sender_id = %s",
            (sender_id,)
        )
        return (await cursor.fetchone())[0]

    async def increase_schedule_counter(self, sender_id: str):
        try:
            await self.connection.execute(
                "UPDATE users SET schedule_counter = schedule_counter + 1 WHERE sender_id = %s",
                (sender_id,)
            )
            await self.connection.commit()
        except psycopg.OperationalError as err:
            log.error(err)
            if err == "the connection is lost":
                self.connection = await Database._connect()
                await self.increase_schedule_counter(sender_id)

    async def increase_homework_counter(self, sender_id: str):
        try:
            await self.connection.execute(
                "UPDATE users SET homework_counter = homework_counter + 1 WHERE sender_id = %s",
                (sender_id,)
            )
            await self.connection.commit()
        except psycopg.OperationalError as err:
            log.error(err)
            if err == "the connection is lost":
                self.connection = await Database._connect()
                await self.increase_homework_counter(sender_id)

    async def increase_marks_counter(self, sender_id: str):
        try:
            await self.connection.execute(
                "UPDATE users SET marks_counter = marks_counter + 1 WHERE sender_id = %s",
                (sender_id,)
            )
            await self.connection.commit()
        except psycopg.OperationalError as err:
            log.error(err)
            if err == "the connection is lost":
                self.connection = await Database._connect()
                await self.increase_marks_counter(sender_id)

    async def increase_holidays_counter(self, sender_id: str):
        try:
            await self.connection.execute(
                "UPDATE users SET holidays_counter = holidays_counter + 1 WHERE sender_id = %s",
                (sender_id,)
            )
            await self.connection.commit()
        except psycopg.OperationalError as err:
            log.error(err)
            if err == "the connection is lost":
                self.connection = await Database._connect()
                await self.increase_holidays_counter(sender_id)

    async def increase_options_counter(self, sender_id: str):
        try:
            await self.connection.execute(
                "UPDATE users SET options_counter = options_counter + 1 WHERE sender_id= %s",
                (sender_id,)
            )
            await self.connection.commit()
        except psycopg.OperationalError as err:
            log.error(err)
            if err == "the connection is lost":
                self.connection = await Database._connect()
                await self.increase_options_counter(sender_id)

    async def increase_help_counter(self, sender_id: str):
        try:
            await self.connection.execute(
                "UPDATE users SET help_counter = help_counter + 1 WHERE sender_id = %s",
                (sender_id,)
            )
            await self.connection.commit()
        except psycopg.OperationalError as err:
            log.error(err)
            if err == "the connection is lost":
                self.connection = await Database._connect()
                await self.increase_help_counter(sender_id)

    async def increase_inline_counter(self, sender_id: str):
        await self.connection.execute(
            "UPDATE users SET inline_counter = inline_counter + 1 WHERE sender_id = %s",
            (sender_id,)
        )
        await self.connection.commit()

    async def crate_table(self):
        await self.connection.execute(
            "CREATE TABLE users ("
            "sender_id VARCHAR(255) PRIMARY KEY,"
            "message_id INTEGER,"
            "schedule_counter INTEGER,"
            "homework_counter INTEGER,"
            "marks_counter INTEGER,"
            "holidays_counter INTEGER,"
            "clear_counter INTEGER,"
            "options_counter INTEGER,"
            "help_counter INTEGER,"
            "about_counter INTEGER,"
            "inline_counter INTEGER"
            ");")
        await self.connection.commit()

    async def add_column(self):
        await self.connection.execute(
            "ALTER TABLE users ADD COLUMN schedule_counter INTEGER"
        )
        await self.connection.commit()

    @property
    def connection(self):
        return self._connection

    @connection.setter
    def connection(self, value):
        self._connection = value