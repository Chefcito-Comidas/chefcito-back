from typing import Any, List


class OpinionsProvider:

   async def create_opinion(self, opinion) -> Any:
       raise Exception("Interface method should not be called")

   async def query_opinions(self, query) -> Any:
       raise Exception("Interface method should not be called")

   async def get_summary(self, restaurant) -> Any:
       raise Exception("Interface method should not be called")

   async def create_new_summary(self, restaurant) -> Any:
       raise Exception("Interface method should not be called")


class OpinionsService:
    
    def __init__(self, provider: OpinionsProvider):
        self.provider = provider

    
    async def create_opinion(self, opinion) -> Any:
        raise Exception("TODO")

    async def query_opinions(self, query) -> List[Any]:
        raise Exception("TODO")

    async def get_summary(self, restaurant) -> Any:
        raise Exception("TODO")

    async def create_new_summary(self, restaurant) -> Any:
        raise Exception("TODO")

class HttpOpinionsProvider(OpinionsProvider):
    pass

class LocalOpinionsProvider(OpinionsProvider):
    pass
