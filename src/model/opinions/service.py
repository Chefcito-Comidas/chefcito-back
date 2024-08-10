from datetime import datetime, timedelta
from typing import Any, List

from src.model.commons.caller import get, post, recover_json_data
from src.model.commons.error import Error
from src.model.opinions.data.base import OpinionsDB
from src.model.opinions.opinion import Opinion
from src.model.opinions.opinion_query import OpinionQuery, OpinionQueryResponse
from src.model.summarizer.service import SummarizerService
from src.model.summarizer.summary_query import SummaryQuery
from src.model.opinions.provider import OpinionsProvider


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

    async def get_summary(self, venue: str) -> Any:
        query = SummaryQuery(venue=venue)
        return await self.summaries.get_summary(query)

    async def create_new_summary(self, venue: str) -> Any:
        return await self.summaries.create_summary(venue, datetime.today() - timedelta(days=14)) 

class HttpOpinionsProvider(OpinionsProvider):

    def __init__(self, url: str):
        self.url = url

    async def create_opinion(self, opinion: Opinion) -> Opinion:
        endpoint = "/opinions"
        body = opinion.model_dump()
        body['date'] = body['date'].__str__()
        response = await post(f"{self.url}{endpoint}", body=body)
        return await recover_json_data(response)

    async def query_opinions(self, query: OpinionQuery) -> OpinionQueryResponse:
        endpoint = "/opinions"
        params = query.model_dump(exclude_none=True)
        if params.get("from_time"):
            params['from_time'] = params['from_time'].__str__()
        if params.get('to_time'):
            params['to_time'] = params['to_time'].__str__()
        response = await get(f"{self.url}{endpoint}", params=params)
        return await recover_json_data(response)

class LocalOpinionsProvider(OpinionsProvider):

    def __init__(self, db: OpinionsDB):
        self.db = db

    async def create_opinion(self, opinion: Opinion) -> Opinion:
        await self.db.store(opinion)

        return opinion

    async def query_opinions(self, query: OpinionQuery) -> OpinionQueryResponse:
        return await self.db.get(query)
