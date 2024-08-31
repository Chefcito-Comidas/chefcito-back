from typing import List, Tuple
from fastapi import Response, status

from src.model.commons.error import Error
from src.model.commons.caller import delete, get, post, put, recover_json_data
from src.model.venues.data.base import VenuesBase
from src.model.venues.data.schema import VenueSchema
from src.model.venues.venue import CreateInfo, Venue

from src.model.venues.update import Update
from src.model.venues.venueQuery import VenueQuery, VenueQueryResult


class VenuesProvider:

    async def create_venue(self, venue: CreateInfo) -> Venue:
        raise Exception("Interface method should not be called")

    async def update_venue(self, venue_id: str, venue_update: Update) -> Venue:
        raise Exception("Interface method should not be called")

    async def get_venues(self, query: VenueQuery) -> VenueQueryResult:
        raise Exception("Interface method should not be called")

    async def delete_venue(self, venue_id: str) -> None:
        raise Exception("Interface method should not be called")

    async def get_venues_near_to(self, localtion: Tuple[str, str]) -> VenueQueryResult:
        raise Exception("Interface method should not be called")

class VenuesService:

    def __init__(self, provider: VenuesProvider):
        self.provider = provider


    async def create_venue(self, venue: CreateInfo, response: Response) -> Venue | Error:
        try:
            value = await self.provider.create_venue(venue)
            return value
        except Exception as e:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return Error.from_exception(e, endpoint="/venues")

    async def update_venue(self, venue: str, update: Update, response: Response) -> Venue | Error:
        try:
            return await self.provider.update_venue(venue, update)
        except Exception as e:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return Error.from_exception(e)


    async def get_venues(self, query: VenueQuery, response: Response) -> VenueQueryResult | Error:
        try:
            return await self.provider.get_venues(query)
        except Exception as e:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return Error.from_exception(e)

    async def delete_venue(self, venue_id: str) -> None:
        try:
            await self.provider.delete_venue(venue_id)
        finally:
            return

    async def get_venues_near_to(self, location: Tuple[str, str], response: Response) -> VenueQueryResult | Error:
        try:
            return await self.provider.get_venues_near_to(location)
        except Exception as e:
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return Error.from_exception(e)

class HttpVenuesProvider(VenuesProvider):
    def __init__(self, service_url: str):
        self.url = service_url

    async def create_venue(self, venue: CreateInfo) -> Venue:
        endpoint = "/venues"
        model = venue.model_dump()
        model['slots'] = [slot.__str__() for slot in model['slots']]
        model['vacations'] = [vacation.__str__() for vacation in model['vacations']]
        response = await post(f"{self.url}{endpoint}", body=model)
        return await recover_json_data(response) 
        

    async def update_venue(self, venue_id: str, venue_update: Update) -> Venue:
        endpoint = "/venues"
        model = venue_update.model_dump()
        if model.get('slots'):
            model['slots'] = [slot.__str__() for slot in model['slots']]
        if model.get('vacations'):
            model['vacations'] = [vacation.__str__() for vacation in model['vacations']]
        response = await put(f"{self.url}{endpoint}/{venue_id}", body=model)
        return await recover_json_data(response) 
        

    async def get_venues(self, query: VenueQuery) -> VenueQueryResult:
        endpoint = "/venues"
        response = await get(f"{self.url}{endpoint}", params=query.model_dump(exclude_none=True))
        return await recover_json_data(response)
    
    async def delete_venue(self, venue_id: str) -> None:
        endpoint = "/venues"
        await delete(f"{self.url}{endpoint}/{venue_id}")
        return  
        

class LocalVenuesProvider(VenuesProvider):
    def __init__(self, base: VenuesBase):
        self.db = base

    async def create_venue(self, venue: CreateInfo) -> Venue:
        persistance = venue.into_venue().persistance()
        response=Venue.from_schema(persistance)
        self.db.store_venue(persistance)
        return response

    async def update_venue(self, venue_id: str, venue_update: Update) -> Venue:
        schema = self.db.get_venue_by_id(venue_id)
        if schema:
            venue = Venue.from_schema(schema)
            venue = venue_update.modify(venue)
            self.db.update_venue(venue.persistance())
            return venue
        raise Exception("Venue does not exist")

    async def get_venues(self, query: VenueQuery) -> VenueQueryResult:
        return query.query(self.db)
    
    async def delete_venue(self, venue_id: str) -> None:
        Venue.delete(venue_id, self.db)
