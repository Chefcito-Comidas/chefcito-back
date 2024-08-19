from datetime import datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel
from src.model.opinions.data.base import OpinionsDB
from src.model.summarizer.summary import Summary

class SummaryQuery(BaseModel):
    venue: str
    limit: int = 1
    skip: int = 0
    
    def __get_oldest_possible_date(self) -> datetime:
        return datetime.today() - timedelta(days=365)

    async def make_query(self, db: OpinionsDB) -> List[Summary]:
       return await db.get_summaries(self.venue, self.__get_oldest_possible_date(), self.limit, self.skip) 

