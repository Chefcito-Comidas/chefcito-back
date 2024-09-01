from datetime import datetime, timedelta
from typing import Any, List

from src.model.commons.caller import get, post, recover_json_data
from src.model.commons.error import Error
from src.model.opinions.data.base import OpinionsDB
from src.model.opinions.opinion import Opinion
from src.model.opinions.opinion_query import OpinionQuery, OpinionQueryResponse
from src.model.summarizer.summary_query import SummaryQuery
from src.model.opinions.provider import OpinionsProvider
from src.model.summarizer.provider import SummarizerService

class OpinionsService:
    
    def __init__(self, provider: OpinionsProvider, summaries: SummarizerService):
        self.provider = provider 
        self.summaries = summaries

    async def create_opinion(self, opinion: Opinion) -> Opinion | Error:
        try:
            await self.provider.create_opinion(opinion)
            return opinion
        except Exception as e:
            return Error.from_exception(e) 

    async def query_opinions(self, query: OpinionQuery) -> OpinionQueryResponse | Error:
        try:
            return await self.provider.query_opinions(query)
        except Exception as e:
            return Error.from_exception(e)

    async def get_summary(self, venue: str, limit: int, skip: int) -> Any:
        query = SummaryQuery(venue=venue,
                             limit=limit,
                             skip=skip)
        return await self.summaries.get_summary(query)

    async def create_new_summary(self, venue: str) -> Any:
        return await self.summaries.create_summary(venue, datetime.today() - timedelta(days=14)) 

