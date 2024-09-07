from typing import Any, Dict, Tuple
from beanie import Document, init_beanie

from src.model.stats.data.user_data import UserDataDocument
from src.model.stats.data.venue_data import VenueDataDocument
from src.model.stats.user_data import UserStatData
from motor.motor_asyncio import AsyncIOMotorClient

from src.model.stats.venue_data import VenueStatData

class StatsDB:
    
    async def update_user_data(self, doc: UserStatData):
        raise Exception("Interface method should not be called")

    async def update_venue_data(self, doc: VenueStatData):
        raise Exception("Interface method should not be called")

    async def get_by_user(self, user: str) -> UserStatData:
        raise Exception("Interface exception should not be called")    

    async def get_by_venue(self, venue: str) -> VenueStatData:
        raise Exception("Interface method should not be called")
    
    async def get_venue_user(self, user: str, venue: str) -> Tuple[UserStatData, VenueStatData]:
        raise Exception("Interface method should not be called")

class MongoStatsDB(StatsDB):
    async def init(self):
        self.db = await init_beanie(database=self.client.db_name, document_models=[UserDataDocument, VenueDataDocument])

    def __init__(self, conn_string: str):
        client = AsyncIOMotorClient(conn_string)
        self.client = client
        self.db = None 

    async def __get_user_doc(self, user: str) -> UserDataDocument:
        doc = await UserDataDocument.find_one(UserDataDocument.user == user)
        if not doc:
            return UserDataDocument(user=user, total=0, canceled=0, expired=0)
        return doc

    async def __get_venue_doc(self, venue: str) -> VenueDataDocument:
        doc = await VenueDataDocument.find_one(VenueDataDocument.venue == venue)
        if not doc:
            return VenueDataDocument.new_document(venue)
        return doc

    async def get_by_user(self, user: str) -> UserStatData:
        doc = await self.__get_user_doc(user)    
        return doc.into_stat_data()

    async def get_by_venue(self, venue: str) -> VenueStatData:
        doc = await self.__get_venue_doc(venue)
        return doc.into_stat_data()

    async def update_user_data(self, doc: UserStatData):
        user = await self.__get_user_doc(doc.user)
        user.update_from(doc)
        await user.save()

    async def update_venue_data(self, doc: VenueStatData):
        venue = await self.__get_venue_doc(doc.venue)
        venue.update_from(doc)
        await venue.save()

    async def get_venue_user(self, user: str, venue: str) -> Tuple[UserStatData, VenueStatData]:
        user_val = self.get_by_user(user) 
        venue_val = self.get_by_venue(venue)
        return await user_val, await venue_val

class MockedStatsDB(StatsDB):

    def __init__(self):
        self.data: Dict[str, Dict[str, Any]] = {}
        self.data['user_data'] = {}
        self.data['venue_data'] = {}

    async def update_user_data(self, doc: UserStatData):
        self.data['user_data'][doc.user] = doc

    async def get_by_user(self, user: str) -> UserStatData:
        return self.data['user_data'].get(user, UserStatData(user=user, total=0, canceled=0, expired=0))                  # type: ignore

    async def update_venue_data(self, doc: VenueStatData):
        self.data['venue_data'][doc.venue] = doc

    async def get_by_venue(self, venue: str) -> VenueStatData:
        return self.data['venue_data'].get(venue, VenueStatData(venue=venue, total=0, canceled=0, expired=0, people=0))  

    async def get_venue_user(self, user: str, venue: str) -> Tuple[UserStatData, VenueStatData]:
        return await self.get_by_user(user), await self.get_by_venue(venue)