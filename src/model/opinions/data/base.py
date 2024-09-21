import asyncio
from datetime import datetime
from typing import Any, Dict, List
from src.model.opinions.data.OpinionSchema import OpinionSchema, SummarySchema
from src.model.opinions.opinion import Opinion
from src.model.opinions.opinion_query import OpinionQuery, OpinionQueryResponse
import motor.motor_asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from beanie.odm.queries.find import FindMany

from src.model.summarizer.summary import Summary


class OpinionsDB:
    
    async def store(self, opinion: Opinion) -> None:
        raise Exception("Interface method should not be called")
    
    async def store_summary(self, summary: Summary) -> None:
        raise Exception("Interface method should not be called")
    
    async def get_total(self, query: OpinionQuery) -> int:
        raise Exception("Interface method should not be called")

    async def get(self, query: OpinionQuery) -> OpinionQueryResponse:
        raise Exception("Interface method should not be called")

    async def get_summaries(self, venue: str, since: datetime, limit: int = 3, skip: int = 0) -> List[Summary]:
        raise Exception("Interface method should not be called")

class MongoOpinionsDB(OpinionsDB):
    
    async def init(self):
        self.db = await init_beanie(database=self.client.db_name, document_models=[OpinionSchema, SummarySchema])

    def __init__(self, conn_string: str):
        client = AsyncIOMotorClient(conn_string)
        self.client = client
        self.db = None 
    
    async def get_total(self, query: OpinionQuery) -> int:
        return await query.total_query() 

    async def store(self, opinion: Opinion) -> None:
        schema = OpinionSchema.from_opinion(opinion)
        await schema.insert()
    
    async def get(self, query: OpinionQuery) -> OpinionQueryResponse:
        result = query.query() 
        
        opinions = list(map(
            lambda x: x.into_opinion(),
            await result.to_list()
            )) if result else []
        total = await self.get_total(query)
        return OpinionQueryResponse(result=opinions, total=total)

    async def store_summary(self, summary: Summary) -> None:
        schema = SummarySchema.from_summary(summary)
        await schema.save()

    async def get_summaries(self, venue: str, since: datetime, limit: int = 1, skip: int = 0) -> List[Summary]:
        query: FindMany[SummarySchema] = SummarySchema.find_many(SummarySchema.venue == venue).\
        find_many(SummarySchema.date.__ge__(since))
        return await query.limit(limit).skip(skip).sort("-date")

class MockedOpinionsDB(OpinionsDB):
    

    def __init__(self):
        self.opinions: Dict[str, Dict[str, Any]] = {}

    async def store(self, opinion: Opinion) -> None:
        
        venue = self.opinions.get(opinion.venue, {}).get('opinions', [])

        if not venue:
            self.opinions[opinion.venue] = {}
        
        venue.append(opinion)
        self.opinions[opinion.venue]['opinions'] = venue
    
    async def get_total(self, query: OpinionQuery) -> int:
        raise Exception("Total should not be called for Mocked Database")

    async def get(self, query: OpinionQuery) -> OpinionQueryResponse:
        if not query.venue:
            return OpinionQueryResponse(result=[], total=0) 

        value = self.opinions.get(query.venue, {})
        value = value.get('opinions', [])
        venue: List[Opinion] = value if value != None else [] 
        
        if query.from_date != None:
            venue = list(filter(
                lambda op: op.date != None and op.date >= query.from_date,  # type: ignore
                venue
                )
                    )
        if query.to_date != None:
            venue = list(filter(
                lambda op: op.date != None and op.date <= query.to_date, # type: ignore
                venue
                ))


        return OpinionQueryResponse(result=venue, total=len(venue)) 

    async def store_summary(self, summary: Summary) -> None:
        
        venue = self.opinions.get(summary.venue, {}).get('summaries', [])
            
        venue.append(summary)
        self.opinions[summary.venue]['summaries'] = venue

    async def get_summaries(self, venue: str, since: datetime, limit: int = 3, skip: int = 0) -> List[Summary]:
        summaries = self.opinions.get(venue, {}).get('summaries', [])
        summaries = filter(
                lambda summ: summ.date >= since,
                summaries
                )
        return list(summaries)[skip:limit+skip]

         
