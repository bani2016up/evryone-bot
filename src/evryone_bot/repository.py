from pathlib import Path

import aiosqlite


class MemberRepository:
    def __init__(self, database_path: Path) -> None:
        self._database_path = database_path

    async def initialize(self) -> None:
        async with aiosqlite.connect(self._database_path) as connection:
            await connection.execute(
                """
                CREATE TABLE IF NOT EXISTS chat_members (
                    chat_id INTEGER NOT NULL,
                    user_id INTEGER,
                    username TEXT NOT NULL COLLATE NOCASE,
                    UNIQUE (chat_id, username)
                )
                """
            )
            await connection.execute(
                """
                CREATE UNIQUE INDEX IF NOT EXISTS chat_members_user_id
                ON chat_members (chat_id, user_id)
                WHERE user_id IS NOT NULL
                """
            )
            await connection.commit()

    async def save(self, chat_id: int, user_id: int, username: str | None) -> None:
        async with aiosqlite.connect(self._database_path) as connection:
            if username:
                await connection.execute(
                    "DELETE FROM chat_members WHERE chat_id = ? AND user_id = ?",
                    (chat_id, user_id),
                )
                await connection.execute(
                    """
                    INSERT INTO chat_members (chat_id, user_id, username)
                    VALUES (?, ?, ?)
                    ON CONFLICT (chat_id, username)
                    DO UPDATE SET user_id = excluded.user_id
                    """,
                    (chat_id, user_id, username),
                )
            else:
                await connection.execute(
                    "DELETE FROM chat_members WHERE chat_id = ? AND user_id = ?",
                    (chat_id, user_id),
                )
            await connection.commit()

    async def add_usernames(self, chat_id: int, usernames: list[str]) -> None:
        async with aiosqlite.connect(self._database_path) as connection:
            await connection.executemany(
                """
                INSERT INTO chat_members (chat_id, username)
                VALUES (?, ?)
                ON CONFLICT (chat_id, username) DO NOTHING
                """,
                [(chat_id, username) for username in usernames],
            )
            await connection.commit()

    async def remove(
        self, chat_id: int, user_id: int, username: str | None = None
    ) -> None:
        async with aiosqlite.connect(self._database_path) as connection:
            if username:
                await connection.execute(
                    """
                    DELETE FROM chat_members
                    WHERE chat_id = ? AND (user_id = ? OR username = ?)
                    """,
                    (chat_id, user_id, username),
                )
            else:
                await connection.execute(
                    "DELETE FROM chat_members WHERE chat_id = ? AND user_id = ?",
                    (chat_id, user_id),
                )
            await connection.commit()

    async def migrate_chat(self, old_chat_id: int, new_chat_id: int) -> None:
        if old_chat_id == new_chat_id:
            return

        async with aiosqlite.connect(self._database_path) as connection:
            cursor = await connection.execute(
                "SELECT user_id, username FROM chat_members WHERE chat_id = ?",
                (old_chat_id,),
            )
            for user_id, username in await cursor.fetchall():
                if user_id is not None:
                    await connection.execute(
                        "DELETE FROM chat_members WHERE chat_id = ? AND user_id = ?",
                        (new_chat_id, user_id),
                    )
                await connection.execute(
                    """
                    INSERT INTO chat_members (chat_id, user_id, username)
                    VALUES (?, ?, ?)
                    ON CONFLICT (chat_id, username)
                    DO UPDATE SET user_id = COALESCE(excluded.user_id, user_id)
                    """,
                    (new_chat_id, user_id, username),
                )
            await connection.execute(
                "DELETE FROM chat_members WHERE chat_id = ?", (old_chat_id,)
            )
            await connection.commit()

    async def usernames(self, chat_id: int) -> list[str]:
        async with aiosqlite.connect(self._database_path) as connection:
            cursor = await connection.execute(
                """
                SELECT username
                FROM chat_members
                WHERE chat_id = ?
                ORDER BY username COLLATE NOCASE
                """,
                (chat_id,),
            )
            rows = await cursor.fetchall()
        return [row[0] for row in rows]
