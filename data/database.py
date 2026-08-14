from config import engine
from data.entities import Base


class Database:
    def __init__(self):
        self.base = Base()

    async def init_db(self):
        async with engine.begin() as conn:
            await conn.run_sync(self.base.metadata.create_all)
