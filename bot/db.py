import aiosqlite

from config import DB_FILE


class Db:
    def __init__(self, db_file=DB_FILE):
        self._db_file = db_file


    async def init_db(self):
        async with aiosqlite.connect(self._db_file) as con:
            # Create tables
            await con.executescript("""
                CREATE TABLE IF NOT EXISTS liked (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    quote TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS disliked (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    quote TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS posted (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    quote TEXT NOT NULL
                );
            """)
            return await con.commit()


    async def add_quote(self, quote, table_name):
        async with aiosqlite.connect(self._db_file) as con:
            await con.execute(f"INSERT INTO {table_name} (quote) VALUES (?);",
                              (quote,))
            return await con.commit()


    async def del_quote(self, q_id, table_name="liked"):
        async with aiosqlite.connect(self._db_file) as con:
            await con.execute(f"DELETE FROM {table_name} WHERE id=?;",
                              (q_id,))
            return await con.commit()


    async def get_random_quote(self, table_name="liked"):
        async with aiosqlite.connect(self._db_file) as con:
            async with con.execute(
                f"SELECT id, quote FROM {table_name} ORDER BY RANDOM() LIMIT 1;"
            ) as cursor:
                result = await cursor.fetchone()
                if result:
                    return {"id": result[0], "quote": result[1]}
            return None
