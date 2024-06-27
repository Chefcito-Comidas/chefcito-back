from typing import List
from fastapi import Response, status

from src.model.commons.error import Error
from src.model.venues.venue import Venue
from src.model.venues.update import Update
from src.model.venues.venueQuery import VenueQuery


class VenuesProvider:

    async def create_venue(self, venue: Venue) -> Venue:
        raise Exception("Interface method should not be called")

    async def update_venue(self, venue: Venue, venue_update: Update) -> Venue:
        raise Exception("Interface method should not be called")

    async def get_venues(self, query: VenueQuery) -> List[Venue]:
        raise Exception("Interface method should not be called")


class VenuesService:

    def __init__(self, provider: VenuesProvider):
        self.provider = provider


    async def create_venue(self, venue: Venue, response: Response) -> Venue | Error:
        try:
            return await self.provider.create_venue(venue)
        except Exception as e:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return Error.from_exception(e)

    async def update_venue(self, venue: Venue, update: Update, response: Response) -> Venue | Error:
        try:
            return await self.provider.update_venue(venue, update)
        except Exception as e:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return Error.from_exception(e)


    async def get_venues(self, query: VenueQuery, response: Response) -> List[Venue] | Error:
        try:
            return await self.provider.get_venues(query)
        except Exception as e:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return Error.from_exception(e)




class HttpVenuesProvider(VenuesProvider):
        pass

class LocalVenuesProvider(VenuesProvider):
        pass