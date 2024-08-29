from typing import Any, List

from src.model.commons.caller import get, post, recover_json_data
from src.model.opinions.data.base import OpinionsDB
from src.model.opinions.opinion import Opinion
from src.model.opinions.opinion_query import OpinionQuery, OpinionQueryResponse


class OpinionsProvider:

    async def create_opinion(self, opinion: Opinion) -> Opinion:
       raise Exception("Interface method should not be called")

    async def query_opinions(self, query: OpinionQuery) -> OpinionQueryResponse:
       raise Exception("Interface method should not be called")

    async def get_summary(self, restaurant) -> Any:
       raise Exception("Interface method should not be called")

    async def create_new_summary(self, restaurant) -> Any:
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

    async def query_opinions(self, query: OpinionQuery) -> List[Opinion]:
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
