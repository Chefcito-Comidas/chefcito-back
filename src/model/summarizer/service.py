from datetime import datetime
from typing import Any

from src.model.commons.error import Error
from src.model.opinions.data.base import OpinionsDB
from src.model.opinions.opinion_query import OpinionQuery
from src.model.summarizer.summary import Summary

class SummarizerProvider:
   
    async def get_summary(self, query) -> Summary:
        raise Exception("Interface method should not be called")

    async def create_summary(self, venue: str, since: datetime) -> Summary:
        raise Exception("Interface method should not be called")


class SummarizerService:
    
    def __init__(self, provider: SummarizerProvider):
        self.provider = provider


    async def get_summary(self, query) -> Any:
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
    
    def __init__(self, db: OpinionsDB):
        self.db = db

    async def create_summary(self, venue: str, since: datetime) -> Summary:
        query = OpinionQuery(venue=venue, from_date=since)
        result = await self.db.get(query)
        summary = Summary(venue=venue, text="", date=datetime.today())
        for opinion in result:
            summary.text = summary.text + opinion.opinion
        return summary

class HttpSummarizerProvider(SummarizerProvider):
    pass
