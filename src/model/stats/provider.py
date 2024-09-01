from src.model.stats.data.base import StatsDB
from src.model.stats.data.user_data import UserDataDocument
from src.model.stats.stats_query import StatsQuery
from src.model.stats.stats_update import StatsUpdate


class StatsProvider():
    
    async def update(self, update: StatsUpdate):
        raise Exception("Interface method should not be called")

    async def get_user(self, user: str) -> UserDataDocument:
        raise Exception("Interface method should not be called")

class LocalStatsProvider(StatsProvider):
    
    def __init__(self, db: StatsDB):
        self.db = db

    async def update(self, update: StatsUpdate):
        await update.update(self.db)

    async def get_user(self, query: str) -> UserDataDocument:
        return await self.db.get_by_user(query) 