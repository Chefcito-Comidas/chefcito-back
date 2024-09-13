from beanie import Document
from pydantic import BaseModel

from src.model.stats.data.base import StatsDB
from src.model.stats.user_data import UserStatData


class StatsQuery(BaseModel):
    user: str

    async def query(self, db: StatsDB) -> UserStatData:
        return await db.get_by_user(self.user)