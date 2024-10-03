from datetime import datetime, timedelta, timezone
from typing import Any, List

from src.model.commons.caller import get, post, recover_json_data
from src.model.commons.error import Error
from src.model.commons.logger import Logger
from src.model.opinions.data.base import OpinionsDB
from src.model.opinions.opinion import Opinion
from src.model.opinions.opinion_query import OpinionQuery, OpinionQueryResponse
from src.model.summarizer.provider import SummarizerProvider
from src.model.summarizer.summary import Summary
from src.model.summarizer.summary_query import SummaryQuery


class OpinionsProvider:

    async def create_opinion(self, opinion: Opinion) -> Opinion:
       raise Exception("Interface method should not be called")

    async def query_opinions(self, query: OpinionQuery) -> OpinionQueryResponse:
       raise Exception("Interface method should not be called")

    async def create_venue_summary(self, venue: str) -> Summary:
        raise Exception("Interface method should not be called")
    
    async def get_venue_summary(self, venue: str) -> Summary:
        raise Exception("Interface method should not be called")

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

    async def create_venue_summary(self, venue: str) -> Summary:
        endpoint = f"/summaries/{venue}"
        response = await post(f"{self.url}{endpoint}")
        return await recover_json_data(response)

    async def get_venue_summary(self, venue: str) -> Summary:
        endpoint = f"/summaries/{venue}"
        response = await get(f"{self.url}{endpoint}")
        return await recover_json_data(response)

class LocalOpinionsProvider(OpinionsProvider):

    def __init__(self, db: OpinionsDB, summaries: SummarizerProvider):
        self.db = db
        self.summaries = summaries

    async def create_opinion(self, opinion: Opinion) -> Opinion:
        Logger.info(f"Storing new opinion for venue ==> {opinion.venue}")
        await self.db.store(opinion)
        Logger.info(f"New opinion for venue ==> {opinion.venue} stored")
        return opinion

    async def query_opinions(self, query: OpinionQuery) -> OpinionQueryResponse:
        Logger.info(f"Recieved opinions query: {query}")
        return await self.db.get(query)
    
    async def create_venue_summary(self, venue: str) -> Summary:
        since = datetime.today() - timedelta(days=14)
        summary = await self.summaries.create_summary(venue, since.replace(timezone.utc)) 
        if isinstance(summary, Error):
            raise Exception(summary.description)
        return summary

    async def get_venue_summary(self, venue: str) -> Summary:
        query = SummaryQuery(venue=venue,
                             limit=1,
                             skip=0)
        result = await self.summaries.get_summary(query)
        if isinstance(result, list):
            return result.pop()
        raise Exception(result.description)
