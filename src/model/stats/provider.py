from src.model.commons.caller import get, post, recover_json_data
from src.model.stats.data.base import StatsDB
from src.model.stats.data.user_data import UserDataDocument
from src.model.stats.stats_query import StatsQuery
from src.model.stats.stats_update import StatsUpdate
from src.model.stats.user_data import UserStatData
from src.model.stats.venue_data import VenueStatData

UPDATE_ENDPOINT = "/update-data"
GET_VENUE_DATA_ENDPOINT = "/venue"
GET_USER_DATA_ENDPOINT = "/user"


class StatsProvider():
    
    async def update(self, update: StatsUpdate):
        raise Exception("Interface method should not be called")

    async def get_user(self, user: str) -> UserStatData:
        raise Exception("Interface method should not be called")

    async def get_venue(self, query: str) -> VenueStatData:
        raise Exception("Interface method should not be called")

class HttpStatsProvider(StatsProvider):

    def __init__(self, url: str):
        self.url = url

    async def update(self, update: StatsUpdate):
        endpoint = f"{self.url}{UPDATE_ENDPOINT}"
        await post(endpoint, body=update.model_dump())

    async def get_user(self, user: str) -> UserStatData:
        endpoint = f"{self.url}{GET_USER_DATA_ENDPOINT}/{user}"
        user_data = await get(endpoint)
        return await recover_json_data(user_data) 

    async def get_venue(self, query: str) -> VenueStatData:
        endpoint = f"{self.url}{GET_VENUE_DATA_ENDPOINT}/{query}"
        venue_data = await get(endpoint)
        return await recover_json_data(venue_data)

class LocalStatsProvider(StatsProvider):
    
    def __init__(self, db: StatsDB):
        self.db = db

    async def update(self, update: StatsUpdate):
        await update.update(self.db)

    async def get_venue(self, query: str) -> VenueStatData:
        return await self.db.get_by_venue(query)

    async def get_user(self, query: str) -> UserStatData:
        return await self.db.get_by_user(query) 