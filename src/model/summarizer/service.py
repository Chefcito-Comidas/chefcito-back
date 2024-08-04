from datetime import datetime
from typing import Any

from src.model.commons.error import Error
from src.model.opinions.data.base import OpinionsDB
from src.model.opinions.opinion_query import OpinionQuery
from src.model.summarizer.summary import Summary
from src.model.summarizer.process.algorithm import SummaryAlgorithm
from src.model.summarizer.summary_query import SummaryQuery 

class SummarizerProvider:
   
    async def get_summary(self, query: SummaryQuery) -> Summary:
        raise Exception("Interface method should not be called")

    async def create_summary(self, venue: str, since: datetime) -> Summary:
        raise Exception("Interface method should not be called")


class SummarizerService:
    
    def __init__(self, provider: SummarizerProvider):
        self.provider = provider


    async def get_summary(self, query: SummaryQuery) -> Any:
        try:
            return await self.provider.get_summary(query)
        except Exception as e:
            return Error.from_exception(e)

    async def create_summary(self, venue: str, since: datetime) -> Any:
        try:
            return await self.provider.create_summary(venue, since)
        except Exception as e:
            return Error.from_exception(e)


class LocalSummarizerProvider(SummarizerProvider):
    
    def __init__(self, db: OpinionsDB, algo: SummaryAlgorithm):
        self.db = db
        self.algo = algo

    async def create_summary(self, venue: str, since: datetime) -> Summary:
        return await self.algo.generate(self.db, venue, since)  
    
    async def get_summary(self, query: SummaryQuery) -> Summary:
        return await query.make_query(self.db) 

class HttpSummarizerProvider(SummarizerProvider):
    pass
