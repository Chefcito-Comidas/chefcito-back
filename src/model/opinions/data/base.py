from typing import Dict, List
from src.model.opinions.opinion import Opinion
from src.model.opinions.opinion_query import OpinionQuery


class OpinionsDB:
    
    async def store(self, opinion: Opinion) -> None:
        raise Exception("Interface method should not be called")
    
    async def get(self, query: OpinionQuery) -> List[Opinion]:
        raise Exception("Interface method should not be called")

class MockedOpinionsDB(OpinionsDB):
    

    def __init__(self):
        self.opinions: Dict[str, List[Opinion]] = {}

    async def store(self, opinion: Opinion) -> None:
        
        venue = self.opinions.get(opinion.venue)

        if not venue:
            venue = []
        
        venue.append(opinion)
        self.opinions[opinion.venue] = venue
    
    async def get(self, query: OpinionQuery) -> List[Opinion]:
        if not query.venue:
            return []

        value = self.opinions.get(query.venue, [])
        venue: List[Opinion] = value if value != None else [] 

        return venue
         
