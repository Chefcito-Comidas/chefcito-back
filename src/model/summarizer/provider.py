from datetime import datetime
from typing import List
from src.model.commons.caller import get, post, recover_json_data
from src.model.commons.error import Error
from src.model.summarizer.summary import Summary
from src.model.summarizer.summary_query import SummaryQuery


class SummarizerProvider:
   
    async def get_summary(self, query: SummaryQuery) -> List[Summary]:
        raise Exception("Interface method should not be called")

    async def create_summary(self, venue: str, since: datetime) -> Summary:
        raise Exception("Interface method should not be called")

class SummarizerService:
    
    def __init__(self, provider: SummarizerProvider):
        self.provider = provider


    async def get_summary(self, query: SummaryQuery) -> List[Summary] | Error:
        try:
            return await self.provider.get_summary(query)
        except Exception as e:
            return Error.from_exception(e)

    async def create_summary(self, venue: str, since: datetime) -> Summary | Error:
        try:
            return await self.provider.create_summary(venue, since)
        except Exception as e:
            return Error.from_exception(e)


class HttpSummarizerProvider(SummarizerProvider):
    
    def __init__(self, host: str):
        self.host = host

    async def create_summary(self, venue: str, since: datetime) -> Summary:
        endpoint = f"/summaries/{venue}"
        params = {
            "since": since.__str__()
        }
        response = await post(f"{self.host}{endpoint}", params=params)
        return await recover_json_data(response)

    async def get_summary(self, query: SummaryQuery) -> List[Summary]:
        endpoint = "/summaries"
        model = query.model_dump(exclude_none=True)
        response = await get(f"{self.host}{endpoint}", params=model) 
        return await recover_json_data(response)