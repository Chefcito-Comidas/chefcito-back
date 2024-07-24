import asyncio
from typing import Dict, List
from src.model.opinions.data.OpinionSchema import OpinionSchema
from src.model.opinions.opinion import Opinion
from src.model.opinions.opinion_query import OpinionQuery
import motor.motor_asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie


class OpinionsDB:
    
    async def store(self, opinion: Opinion) -> None:
        raise Exception("Interface method should not be called")
    
    async def get(self, query: OpinionQuery) -> List[Opinion]:
        raise Exception("Interface method should not be called")

class MongoOpinionsDB(OpinionsDB):
    
    async def init(self):
        self.db = await init_beanie(database=self.client.db_name, document_models=[OpinionSchema])

    def __init__(self, conn_string: str):
        client = AsyncIOMotorClient(conn_string)
        self.client = client
        self.db = None 

    async def store(self, opinion: Opinion) -> None:
        schema = OpinionSchema.from_opinion(opinion)
        await schema.insert()
    
    async def get(self, query: OpinionQuery) -> List[Opinion]:
        result = query.query() 
        
        return list(map(
            lambda x: x.into_opinion(),
            await result.to_list()
            )) if result else []

class MockedOpinionsDB(OpinionsDB):
    

    def __init__(self):
        self.opinions: Dict[str, List[Opinion]] = {}

    async def store(self, opinion: Opinion) -> None:
        
        venue = self.opinions.get(opinion.venue)

        if not venue:
            venue = []
        
        venue.append(opinion)
        self.opinions[opinion.venue] = venue
    
    async def get(self, query: OpinionQuery) -> List[Opinion]:
        if not query.venue:
            return []

        value = self.opinions.get(query.venue, [])
        venue: List[Opinion] = value if value != None else [] 

        return venue
         
