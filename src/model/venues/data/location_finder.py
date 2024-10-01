import asyncio
from typing import List, Tuple
from src.model.commons.distance import DistanceRanker, LocalPosition
from src.model.venues.data.base import RelBase, VenuesBase
from src.model.venues.venue import Venue
from src.model.venues.venueQuery import VenueDistance, VenueQuery

RANKER_LIMIT = 1000

class Ranker:

    def __init__(self, database: VenuesBase, location: Tuple[str, str]):
        self.initial_point = LocalPosition("ranker", location[0], location[1])
        self.database = database
        self.base_query = VenueQuery(
            limit=RANKER_LIMIT            
        )

    async def rank(self) -> List[VenueDistance]:
        event_loop = asyncio.get_event_loop()
        first_result = await event_loop.run_in_executor(None, self.base_query.query, self.database)
        loops = (first_result.total // RANKER_LIMIT)
        rank = DistanceRanker(self.initial_point)
        rank.add_batch([value.get_location() for value in first_result.result]) 
        for i in range(loops):
            self.base_query.start = (1 + i) * RANKER_LIMIT
            result = await event_loop.run_in_executor(None, self.base_query.query, self.database)
            rank.add_batch([value.get_location() for value in result.result])
        return list(
                map(lambda x: VenueDistance(venue=Venue.from_schema(x[0]),distance=x[1]), #type: ignore 
                filter(lambda x: x != None, 
                       [(self.database.get_venue_by_id(venue.id),distance) for (venue, distance) in await event_loop.run_in_executor(None, rank.sort)])
                )
        )
