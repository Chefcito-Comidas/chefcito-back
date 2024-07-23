from typing import Any, List

from src.model.opinions.data.base import OpinionsDB
from src.model.opinions.opinion import Opinion
from src.model.opinions.opinion_query import OpinionQuery


class OpinionsProvider:

    async def create_opinion(self, opinion: Opinion) -> Opinion:
       raise Exception("Interface method should not be called")

    async def query_opinions(self, query: OpinionQuery) -> List[Opinion]:
       raise Exception("Interface method should not be called")

    async def get_summary(self, restaurant) -> Any:
       raise Exception("Interface method should not be called")

    async def create_new_summary(self, restaurant) -> Any:
       raise Exception("Interface method should not be called")


class OpinionsService:
    
    def __init__(self, provider: OpinionsProvider):
        self.provider = provider
    
    async def create_opinion(self, opinion) -> Any:
        raise Exception("TODO")

    async def query_opinions(self, query) -> List[Any]:
        raise Exception("TODO")

    async def get_summary(self, restaurant) -> Any:
        raise Exception("TODO")

    async def create_new_summary(self, restaurant) -> Any:
        raise Exception("TODO")

class HttpOpinionsProvider(OpinionsProvider):
    pass

class LocalOpinionsProvider(OpinionsProvider):

    def __init__(self, db: OpinionsDB):
        self.db = db

    async def create_opinion(self, opinion: Opinion) -> Opinion:
        await self.db.store(opinion)

        return opinion

    async def query_opinions(self, query: OpinionQuery) -> List[Opinion]:
        return await self.db.get(query)
