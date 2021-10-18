#!/usr/bin/python3.10

import psycopg
from constants import HOST_SQL, USER_SQL, DATABASE_SQL, PASSWORD_SQL


class Database:
    """
    Class for working with relational DB
    """

    def __init__(self):
        self.connection: psycopg.AsyncConnection = ...

    @staticmethod
    async def create():
        self = Database()
        self.connection = await psycopg.AsyncConnection.connect(
            host=HOST_SQL, user=USER_SQL, dbname=DATABASE_SQL, password=PASSWORD_SQL, sslmode="require"
        )
        return self

    async def get_users(self) -> list:
        cursor = await self.connection.execute(
            "SELECT sender_id FROM users"
        )
        return await cursor.fetchall()

    async def is_inited(self, sender_id: str) -> str:
        cursor = await self.connection.execute(
            "SELECT sender_id FROM users WHERE sender_id = %s",
            (sender_id,)
        )
        return await cursor.fetchone()

    async def init_user(self, sender_id: str):
        await self.connection.execute(
            "INSERT INTO users ("
            "sender_id, message_id, schedule_counter, homework_counter, marks_counter, holidays_counter, "
            "clear_counter, options_counter, help_counter, about_counter, inline_counter"
            ") VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (sender_id, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        )
        await self.connection.commit()

    async def reset_analytics(self):
        await self.connection.execute(
            "UPDATE users SET "
            "schedule_counter = %s, homework_counter = %s, marks_counter = %s, holidays_counter = %s, "
            "clear_counter = %s, options_counter = %s, help_counter = %s, about_counter = %s, inline_counter = %s",
            (0, 0, 0, 0, 0, 0, 0, 0, 0)
        )
        await self.connection.commit()

    async def get_message_id(self, sender_id: str) -> int:
        cursor = await self.connection.execute(
            "SELECT message_id FROM users WHERE sender_id = %s",
            (sender_id,)
        )
        return (await cursor.fetchone())[0]

        # with self.connection.cursor() as cursor:
        #     cursor.execute(
        #         "SELECT message_id FROM users WHERE sender_id = %s",
        #         (sender_id,)
        #     )
        #     return cursor.fetchone()[0]

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

    async def get_clear_counter(self, sender_id: str) -> int:
        cursor = await self.connection.execute(
            "SELECT clear_counter FROM users WHERE sender_id = %s",
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

    async def get_about_counter(self, sender_id: str) -> int:
        cursor = await self.connection.execute(
            "SELECT about_counter FROM users WHERE sender_id = %s",
            (sender_id,)
        )
        return (await cursor.fetchone())[0]

    async def get_inline_counter(self, sender_id: str) -> int:
        cursor = await self.connection.execute(
            "SELECT inline_counter FROM users WHERE sender_id = %s",
            (sender_id,)
        )
        return (await cursor.fetchone())[0]

    async def set_message_id(self, sender_id: str, message_id: int):
        await self.connection.execute(
            "UPDATE users SET message_id = %s WHERE sender_id = %s",
            (message_id, sender_id)
        )
        await self.connection.commit()

    async def increase_schedule_counter(self, sender_id: str):
        await self.connection.execute(
            "UPDATE users SET schedule_counter = schedule_counter + 1 WHERE sender_id = %s",
            (sender_id,)
        )
        await self.connection.commit()

    async def increase_homework_counter(self, sender_id: str):
        await self.connection.execute(
            "UPDATE users SET homework_counter = homework_counter + 1 WHERE sender_id = %s",
            (sender_id,)
        )
        await self.connection.commit()

    async def increase_marks_counter(self, sender_id: str):
        await self.connection.execute(
            "UPDATE users SET marks_counter = marks_counter + 1 WHERE sender_id = %s",
            (sender_id,)
        )
        await self.connection.commit()

    async def increase_holidays_counter(self, sender_id: str):
        await self.connection.execute(
            "UPDATE users SET holidays_counter = holidays_counter + 1 WHERE sender_id = %s",
            (sender_id,)
        )
        await self.connection.commit()

    async def increase_clear_counter(self, sender_id: str):
        await self.connection.execute(
            "UPDATE users SET clear_counter = clear_counter + 1 WHERE sender_id = %s",
            (sender_id,)
        )
        await self.connection.commit()

    async def increase_options_counter(self, sender_id: str):
        await self.connection.execute(
            "UPDATE users SET options_counter = options_counter + 1 WHERE sender_id= %s",
            (sender_id,)
        )
        await self.connection.commit()

    async def increase_help_counter(self, sender_id: str):
        await self.connection.execute(
            "UPDATE users SET help_counter = help_counter + 1 WHERE sender_id = %s",
            (sender_id,)
        )
        await self.connection.commit()

    async def increase_about_counter(self, sender_id: str):
        await self.connection.execute(
            "UPDATE users SET about_counter = about_counter + 1 WHERE sender_id = %s",
            (sender_id,)
        )
        await self.connection.commit()

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
