from typing import Any, Dict
from beanie import Document, init_beanie

from src.model.stats.data.user_data import UserDataDocument
from src.model.stats.user_data import UserStatData
from motor.motor_asyncio import AsyncIOMotorClient

class StatsDB:
    
    async def update_user_data(self, doc: UserStatData):
        raise Exception("Interface method should not be called")
    
    async def get_by_user(self, user: str) -> UserStatData:
        raise Exception("Interface exception should not be called")    


class MongoStatsDB(StatsDB):
    async def init(self):
        self.db = await init_beanie(database=self.client.db_name, document_models=[UserDataDocument])

    def __init__(self, conn_string: str):
        client = AsyncIOMotorClient(conn_string)
        self.client = client
        self.db = None 

    async def __get_user_doc(self, user: str) -> UserDataDocument:
        doc = await UserDataDocument.find_one(UserDataDocument.user == user)
        if not doc:
            return UserDataDocument(user=user, total=0, canceled=0, expired=0)
        return doc

    async def get_by_user(self, user: str) -> UserStatData:
        doc = await self.__get_user_doc(user)    
        return doc.into_stat_data()

    async def update_user_data(self, doc: UserStatData):
        user = await self.__get_user_doc(doc.user)
        user.update_from(doc)
        await user.save()

class MockedStatsDB(StatsDB):

    def __init__(self):
        self.data: Dict[str, Dict[str, Any]] = {}
        self.data['user_data'] = {}


    async def update_user_data(self, doc: UserStatData):
        self.data['user_data'][doc.user] = doc

    async def get_by_user(self, user: str) -> UserStatData:
        return self.data['user_data'].get(user, UserStatData(user=user, total=0, canceled=0, expired=0))                  # type: ignore
    
