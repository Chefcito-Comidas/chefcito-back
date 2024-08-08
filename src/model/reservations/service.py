from datetime import datetime
from typing import List
from fastapi import Response, status

from src.model.commons.caller import delete, get, post, put, recover_json_data
from src.model.commons.error import Error
from src.model.reservations.data.base import ReservationsBase
from src.model.reservations.data.schema import ReservationSchema
from src.model.reservations.reservation import CreateInfo, Reservation
from src.model.reservations.update import Update
from src.model.reservations.reservationQuery import ReservationQuery, ReservationQueryResponse
from src.model.venues.service import VenuesProvider
from src.model.venues.venueQuery import VenueQuery


class ReservationsProvider:
    
    async def create_reservation(self, reservation: CreateInfo) -> Reservation:
        raise Exception("Interface method should not be called")

    async def update_reservation(self, reservation_id: str, reservation_update: Update) -> Reservation:
        raise Exception("Interface method should not be called")
    
    async def get_reservations(self, query: ReservationQuery) -> ReservationQueryResponse:
        raise Exception("Interface method should not be called")
    
    async def delete_reservation(self, reservation_id: str) -> None:
        raise Exception("Interface method should not be called")

class ReservationsService:

    def __init__(self, provider: ReservationsProvider):
        self.provider = provider

    
    async def create_reservation(self, reservation: CreateInfo, response: Response) -> Reservation | Error:
        try:
           return await self.provider.create_reservation(reservation)
        except Exception as e:
           response.status_code = status.HTTP_400_BAD_REQUEST
           return Error.from_exception(e, endpoint="/reservations")
    
    async def update_reservation(self, reservation: str, update: Update, response: Response) -> Reservation | Error:
        try:
           return await self.provider.update_reservation(reservation, update)
        except Exception as e:
           response.status_code = status.HTTP_400_BAD_REQUEST
           return Error.from_exception(e)
    
    async def get_reservations(self, query: ReservationQuery, response: Response) -> ReservationQueryResponse | Error:
        try:
           print(f"SEARCHING WITH: {query}")
           return await self.provider.get_reservations(query)
        except Exception as e:
           response.status_code = status.HTTP_400_BAD_REQUEST
           return Error.from_exception(e)
    
    async def delete_reservation(self, reservation_id: str) -> None:
        try:
            await self.provider.delete_reservation(reservation_id)
        finally:
            return


class HttpReservationsProvider(ReservationsProvider):
    def __init__(self, service_url: str):
        self.url = service_url

    async def create_reservation(self, reservation: CreateInfo) -> Reservation:
        endpoint = "/reservations"
        body = reservation.model_dump()
        body['time'] = body['time'].__str__()
        response = await post(f"{self.url}{endpoint}", body=body)
        data = await recover_json_data(response) 
        data['time'] = datetime.fromisoformat(data['time'])
        return data

    async def update_reservation(self, reservation_id: str, reservation_update: Update) -> Reservation:
        endpoint = "/reservations"
        body = reservation_update.model_dump(exclude_none=True)
        body['time'] = body['time'].__str__()
        response = await put(f"{self.url}{endpoint}/{reservation_id}", body=body)
        data = await recover_json_data(response) 
        data['time'] = datetime.fromisoformat(data['time'])
        return data

    async def get_reservations(self, query: ReservationQuery) -> ReservationQueryResponse:
        endpoint = "/reservations"
        body = query.model_dump(exclude_none=True)
        if body.get('from_time'):
            body['from_time'] = body['from_time'].__str__() 
        if body.get('to_time'):
            body['to_time'] = body['to_time'].__str__() 
        response = await get(f"{self.url}{endpoint}", params=body)
        return await recover_json_data(response)

    async def delete_reservation(self, reservation_id: str) -> None:
        endpoint = "/reservations"
        await delete(f"{self.url}{endpoint}/{reservation_id}")
        return  

class LocalReservationsProvider(ReservationsProvider):
    
    def __init__(self, base: ReservationsBase, venues: VenuesProvider):
        self.db = base
        self.venues = venues
    
    async def _find_venue(self, venue_id: str) -> bool:
        query = VenueQuery(id=venue_id)
        result = await self.venues.get_venues(query)
        return len(result) != 0

    async def create_reservation(self, reservation: CreateInfo) -> Reservation:
        if not await self._find_venue(reservation.venue):
            raise Exception("Venue does not exist")
        persistance = reservation.into_reservation().persistance()
        response = Reservation.from_schema(persistance)
        self.db.store_reservation(persistance)
        return response 

    async def update_reservation(self, reservation_id: str, reservation_update: Update) -> Reservation:
        schema = self.db.get_reservation_by_id(reservation_id)
        if schema:
            reservation = Reservation.from_schema(schema)
            reservation = reservation_update.modify(reservation)
            self.db.update_reservation(reservation.persistance())
            return reservation
        raise Exception("Reservation does not exist")

    async def get_reservations(self, query: ReservationQuery) -> ReservationQueryResponse:
        return query.query(self.db)

    async def delete_reservation(self, reservation_id: str) -> None:
        Reservation.delete(reservation_id, self.db)
