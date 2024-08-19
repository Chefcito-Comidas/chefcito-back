from datetime import datetime
from typing import Any, List

from src.model.commons.error import Error
from src.model.opinions.data.base import OpinionsDB
from src.model.opinions.opinion_query import OpinionQuery
from src.model.summarizer.provider import SummarizerProvider
from src.model.summarizer.summary import Summary
from src.model.summarizer.process.algorithm import SummaryAlgorithm
from src.model.summarizer.summary_query import SummaryQuery 
from src.model.commons.caller import get, post, recover_json_data




class LocalSummarizerProvider(SummarizerProvider):
    
    def __init__(self, db: OpinionsDB, algo: SummaryAlgorithm):
        self.db = db
        self.algo = algo

    async def create_summary(self, venue: str, since: datetime) -> Summary:
        return await self.algo.generate(self.db, venue, since)  
    
    async def get_summary(self, query: SummaryQuery) -> List[Summary]:
        return await query.make_query(self.db) 
