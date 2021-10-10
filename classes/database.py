#!/usr/bin/python3.10

class Database:
    """
    Class for working with relational DB
    """

    def __init__(self, conn, c):
        self.connection = conn
        self.cursor = c

    async def get_message(self, sender_id: str) -> int:
        with self.connection:
            self.cursor.execute(
                "SELECT message_id FROM messages WHERE sender_id = %s",
                (sender_id,)
            )
            return self.cursor.fetchone()[0]

    async def set_message(self, sender_id: str, message_id: int):
        with self.connection:
            self.cursor.execute(
                "UPDATE messages SET message_id = %s WHERE sender_id = %s",
                (message_id, sender_id)
            )

    async def is_inited(self, sender_id: str) -> str:
        with self.connection:
            self.cursor.execute(
                "SELECT sender_id FROM messages WHERE sender_id = %s",
                (sender_id,)
            )
            return self.cursor.fetchone()

    async def init_user(self, sender_id: str):
        with self.connection:
            self.cursor.execute(
                "INSERT INTO messages (sender_id, message_id) VALUES (%s, %s)",
                (sender_id, None)
            )

    def crate_table(self):
        with self.connection:
            self.cursor.execute("""
                create table messages (
                    sender_id VARCHAR(255) primary key,
                    message_id INTEGER
                );""")
