from datetime import datetime, timedelta, timezone
from typing import List, Optional
from pydantic import BaseModel
from src.model.opinions.data.base import OpinionsDB
from src.model.opinions.opinion_query import OpinionQuery, OpinionQueryResponse
from src.model.summarizer.process.algorithm import SummaryAlgorithm
from src.model.summarizer.summary import Summary

class SummaryQuery(BaseModel):
    venue: str
    limit: int = 1
    skip: int = 0
    
    def __get_oldest_possible_date(self) -> datetime:
        return (datetime.today() - timedelta(days=45)).replace(tzinfo=timezone.utc)
    
    def __get_last_15_days(self) -> datetime:
        return (datetime.today() - timedelta(days=15)).replace(tzinfo=timezone.utc)

    async def __get_query(self, db: OpinionsDB) -> int:
        query = OpinionQuery(
                venue=self.venue,
                from_date=(datetime.today() - timedelta(days=45)).replace(tzinfo=timezone.utc)
                )
        result = await db.get(query) 
        return result.total

    async def create_if_enough(self, db: OpinionsDB, algo: SummaryAlgorithm) -> List[Summary]:
        summary = Summary(venue=self.venue,
                          text="No hay un resumen para este restaurant aun",
                          date=self.__get_last_15_days())
        if await self.__get_query(db) > 4:
            summary = await algo.generate(db, self.venue, self.__get_last_15_days())
        return [summary]

    async def make_query(self, db: OpinionsDB) -> List[Summary]:
       return await db.get_summaries(self.venue, self.__get_oldest_possible_date(), self.limit, self.skip) 

