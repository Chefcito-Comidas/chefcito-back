from typing import Any, Dict
from beanie import Document

from src.model.stats.data.user_data import UserDataDocument
from src.model.stats.user_data import UserStatData


class StatsDB:
    
    async def update_user_data(self, doc: UserStatData):
        raise Exception("Interface method should not be called")
    
    async def get_by_user(self, user: str) -> UserStatData:
        raise Exception("Interface exception should not be called")    


class MockedStatsDB(StatsDB):

    def __init__(self):
        self.data: Dict[str, Dict[str, Any]] = {}
        self.data['user_data'] = {}


    async def update_user_data(self, doc: UserStatData):
        self.data['user_data'][doc.user] = doc

    async def get_by_user(self, user: str) -> UserStatData:
        return self.data['user_data'].get(user, UserStatData(user=user, total=0, canceled=0, expired=0))                  # type: ignore
    
