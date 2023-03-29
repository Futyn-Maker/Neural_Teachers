import aiosqlite

from loguru import logger

from config import DB_FILE


class Db:
    def __init__(self, db_file=DB_FILE):
        self._db_file = db_file


    async def init_db(self):
        async with aiosqlite.connect(self._db_file) as con:
            logger.debug(f"Connected to database {self._db_file}")
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
            logger.debug(f"Connected to database {self._db_file}")
            await con.execute(f"INSERT INTO {table_name} (quote) VALUES (?);",
                              (quote,))
            logger.debug(f"Entry {quote} inserted into {table_name}")
            return await con.commit()


    async def del_quote(self, q_id, table_name="liked"):
        async with aiosqlite.connect(self._db_file) as con:
            logger.debug(f"Connected to database {self._db_file}")
            await con.execute(f"DELETE FROM {table_name} WHERE id=?;",
                              (q_id,))
            logger.debug(f"Entry with ID {q_id} deleted from {table_name}")
            return await con.commit()


    async def get_random_quote(self, table_name="liked"):
        async with aiosqlite.connect(self._db_file) as con:
            logger.debug(f"Connected to database {self._db_file}")
            async with con.execute(
                f"SELECT id, quote FROM {table_name} ORDER BY RANDOM() LIMIT 1;"
            ) as cursor:
                result = await cursor.fetchone()
                if result:
                    logger.debug(f"Got from {table_name}: {result}")
                    return {"id": result[0], "quote": result[1]}
            logger.debug(f"No entries in {table_name}")
            return None
