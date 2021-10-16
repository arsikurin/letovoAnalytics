#!/usr/bin/python3.10

class Database:
    """
    Class for working with relational DB
    """

    def __init__(self, conn, c):
        self.connection = conn
        self.cursor = c

    async def is_inited(self, sender_id: str) -> str:
        with self.connection:
            self.cursor.execute(
                "SELECT sender_id FROM users WHERE sender_id = %s",
                (sender_id,)
            )
            return self.cursor.fetchone()

    async def init_user(self, sender_id: str):
        with self.connection:
            self.cursor.execute(
                "INSERT INTO users ("
                "sender_id, message_id, schedule_counter, homework_counter, marks_counter, holidays_counter, "
                "clear_counter, options_counter, help_counter, about_counter, inline_counter"
                ") VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (sender_id, None, None, None, None, None, None, None, None, None, None)
            )

    async def get_message_id(self, sender_id: str) -> int:
        with self.connection:
            self.cursor.execute(
                "SELECT message_id FROM users WHERE sender_id = %s",
                (sender_id,)
            )
            return self.cursor.fetchone()[0]

    async def get_schedule_counter(self, sender_id: str) -> int:
        with self.connection:
            self.cursor.execute(
                "SELECT schedule_counter FROM users WHERE sender_id = %s",
                (sender_id,)
            )
            return self.cursor.fetchone()[0]

    async def get_homework_counter(self, sender_id: str) -> int:
        with self.connection:
            self.cursor.execute(
                "SELECT homework_counter FROM users WHERE sender_id = %s",
                (sender_id,)
            )
            return self.cursor.fetchone()[0]

    async def get_marks_counter(self, sender_id: str) -> int:
        with self.connection:
            self.cursor.execute(
                "SELECT marks_counter FROM users WHERE sender_id = %s",
                (sender_id,)
            )
            return self.cursor.fetchone()[0]

    async def get_holidays_counter(self, sender_id: str) -> int:
        with self.connection:
            self.cursor.execute(
                "SELECT holidays_counter FROM users WHERE sender_id = %s",
                (sender_id,)
            )
            return self.cursor.fetchone()[0]

    async def get_clear_counter(self, sender_id: str) -> int:
        with self.connection:
            self.cursor.execute(
                "SELECT clear_counter FROM users WHERE sender_id = %s",
                (sender_id,)
            )
            return self.cursor.fetchone()[0]

    async def get_options_counter(self, sender_id: str) -> int:
        with self.connection:
            self.cursor.execute(
                "SELECT options_counter FROM users WHERE sender_id = %s",
                (sender_id,)
            )
            return self.cursor.fetchone()[0]

    async def get_help_counter(self, sender_id: str) -> int:
        with self.connection:
            self.cursor.execute(
                "SELECT help_counter FROM users WHERE sender_id = %s",
                (sender_id,)
            )
            return self.cursor.fetchone()[0]

    async def get_about_counter(self, sender_id: str) -> int:
        with self.connection:
            self.cursor.execute(
                "SELECT about_counter FROM users WHERE sender_id = %s",
                (sender_id,)
            )
            return self.cursor.fetchone()[0]

    async def get_inline_counter(self, sender_id: str) -> int:
        with self.connection:
            self.cursor.execute(
                "SELECT inline_counter FROM users WHERE sender_id = %s",
                (sender_id,)
            )
            return self.cursor.fetchone()[0]

    async def get_schedule_counter_daily(self, sender_id: str) -> int:
        with self.connection:
            self.cursor.execute(
                "SELECT schedule_counter_daily FROM users WHERE sender_id = %s",
                (sender_id,)
            )
            return self.cursor.fetchone()[0]

    async def get_homework_counter_daily(self, sender_id: str) -> int:
        with self.connection:
            self.cursor.execute(
                "SELECT homework_counter_daily FROM users WHERE sender_id = %s",
                (sender_id,)
            )
            return self.cursor.fetchone()[0]

    async def get_marks_counter_daily(self, sender_id: str) -> int:
        with self.connection:
            self.cursor.execute(
                "SELECT marks_counter_daily FROM users WHERE sender_id = %s",
                (sender_id,)
            )
            return self.cursor.fetchone()[0]

    async def get_holidays_counter_daily(self, sender_id: str) -> int:
        with self.connection:
            self.cursor.execute(
                "SELECT holidays_counter_daily FROM users WHERE sender_id = %s",
                (sender_id,)
            )
            return self.cursor.fetchone()[0]

    async def get_clear_counter_daily(self, sender_id: str) -> int:
        with self.connection:
            self.cursor.execute(
                "SELECT clear_counter_daily FROM users WHERE sender_id = %s",
                (sender_id,)
            )
            return self.cursor.fetchone()[0]

    async def get_options_counter_daily(self, sender_id: str) -> int:
        with self.connection:
            self.cursor.execute(
                "SELECT options_counter_daily FROM users WHERE sender_id = %s",
                (sender_id,)
            )
            return self.cursor.fetchone()[0]

    async def get_help_counter_daily(self, sender_id: str) -> int:
        with self.connection:
            self.cursor.execute(
                "SELECT help_counter_daily FROM users WHERE sender_id = %s",
                (sender_id,)
            )
            return self.cursor.fetchone()[0]

    async def get_about_counter_daily(self, sender_id: str) -> int:
        with self.connection:
            self.cursor.execute(
                "SELECT about_counter_daily FROM users WHERE sender_id = %s",
                (sender_id,)
            )
            return self.cursor.fetchone()[0]

    async def get_inline_counter_daily(self, sender_id: str) -> int:
        with self.connection:
            self.cursor.execute(
                "SELECT inline_counter_daily FROM users WHERE sender_id = %s",
                (sender_id,)
            )
            return self.cursor.fetchone()[0]

    async def set_message_id(self, sender_id: str, message_id: int):
        with self.connection:
            self.cursor.execute(
                "UPDATE users SET message_id = %s WHERE sender_id = %s",
                (message_id, sender_id)
            )

    async def set_schedule_counter(self, sender_id: str, schedule_counter: int):
        with self.connection:
            self.cursor.execute(
                "UPDATE users SET schedule_counter = %s WHERE sender_id = %s",
                (schedule_counter, sender_id)
            )

    async def set_homework_counter(self, sender_id: str, homework_counter: int):
        with self.connection:
            self.cursor.execute(
                "UPDATE users SET homework_counter = %s WHERE sender_id = %s",
                (homework_counter, sender_id)
            )

    async def set_marks_counter(self, sender_id: str, marks_counter: int):
        with self.connection:
            self.cursor.execute(
                "UPDATE users SET marks_counter = %s WHERE sender_id = %s",
                (marks_counter, sender_id)
            )

    async def set_holidays_counter(self, sender_id: str, holidays_counter: int):
        with self.connection:
            self.cursor.execute(
                "UPDATE users SET holidays_counter = %s WHERE sender_id = %s",
                (holidays_counter, sender_id)
            )

    async def set_clear_counter(self, sender_id: str, clear_counter: int):
        with self.connection:
            self.cursor.execute(
                "UPDATE users SET clear_counter = %s WHERE sender_id = %s",
                (clear_counter, sender_id)
            )

    async def set_options_counter(self, sender_id: str, options_counter: int):
        with self.connection:
            self.cursor.execute(
                "UPDATE users SET options_counter = %s WHERE sender_id = %s",
                (options_counter, sender_id)
            )

    async def set_help_counter(self, sender_id: str, help_counter: int):
        with self.connection:
            self.cursor.execute(
                "UPDATE users SET help_counter = %s WHERE sender_id = %s",
                (help_counter, sender_id)
            )

    async def set_about_counter(self, sender_id: str, about_counter: int):
        with self.connection:
            self.cursor.execute(
                "UPDATE users SET about_counter = %s WHERE sender_id = %s",
                (about_counter, sender_id)
            )

    async def set_inline_counter(self, sender_id: str, inline_counter: int):
        with self.connection:
            self.cursor.execute(
                "UPDATE users SET inline_counter = %s WHERE sender_id = %s",
                (inline_counter, sender_id)
            )

    async def set_schedule_counter_daily(self, sender_id: str, schedule_counter_daily: int):
        with self.connection:
            self.cursor.execute(
                "UPDATE users SET schedule_counter_daily = %s WHERE sender_id = %s",
                (schedule_counter_daily, sender_id)
            )

    async def set_homework_counter_daily(self, sender_id: str, homework_counter_daily: int):
        with self.connection:
            self.cursor.execute(
                "UPDATE users SET homework_counter_daily = %s WHERE sender_id = %s",
                (homework_counter_daily, sender_id)
            )

    async def set_marks_counter_daily(self, sender_id: str, marks_counter_daily: int):
        with self.connection:
            self.cursor.execute(
                "UPDATE users SET marks_counter_daily = %s WHERE sender_id = %s",
                (marks_counter_daily, sender_id)
            )

    async def set_holidays_counter_daily(self, sender_id: str, holidays_counter_daily: int):
        with self.connection:
            self.cursor.execute(
                "UPDATE users SET holidays_counter_daily = %s WHERE sender_id = %s",
                (holidays_counter_daily, sender_id)
            )

    async def set_clear_counter_daily(self, sender_id: str, clear_counter_daily: int):
        with self.connection:
            self.cursor.execute(
                "UPDATE users SET clear_counter_daily = %s WHERE sender_id = %s",
                (clear_counter_daily, sender_id)
            )

    async def set_options_counter_daily(self, sender_id: str, options_counter_daily: int):
        with self.connection:
            self.cursor.execute(
                "UPDATE users SET options_counter_daily = %s WHERE sender_id = %s",
                (options_counter_daily, sender_id)
            )

    async def set_help_counter_daily(self, sender_id: str, help_counter_daily: int):
        with self.connection:
            self.cursor.execute(
                "UPDATE users SET help_counter_daily = %s WHERE sender_id = %s",
                (help_counter_daily, sender_id)
            )

    async def set_about_counter_daily(self, sender_id: str, about_counter_daily: int):
        with self.connection:
            self.cursor.execute(
                "UPDATE users SET about_counter_daily = %s WHERE sender_id = %s",
                (about_counter_daily, sender_id)
            )

    async def set_inline_counter_daily(self, sender_id: str, inline_counter_daily: int):
        with self.connection:
            self.cursor.execute(
                "UPDATE users SET inline_counter_daily = %s WHERE sender_id = %s",
                (inline_counter_daily, sender_id)
            )

    async def crate_table(self):
        with self.connection:
            self.cursor.execute(
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
                "inline_counter INTEGER,"
                "schedule_counter_daily INTEGER,"
                "homework_counter_daily INTEGER,"
                "marks_counter_daily INTEGER,"
                "holidays_counter_daily INTEGER,"
                "clear_counter_daily INTEGER,"
                "options_counter_daily INTEGER,"
                "help_counter_daily INTEGER,"
                "about_counter_daily INTEGER,"
                "inline_counter_daily INTEGER"
                ");")

    async def add_column(self):
        with self.connection:
            self.cursor.execute(
                "ALTER TABLE users ADD COLUMN schedule_counter INTEGER"
            )
