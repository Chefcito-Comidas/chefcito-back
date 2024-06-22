from typing import List
from fastapi import Response, status

from src.model.commons.caller import delete, get, post, put, recover_json_data
from src.model.commons.error import Error
from src.model.reservations.data.base import ReservationsBase
from src.model.reservations.data.schema import ReservationSchema
from src.model.reservations.reservation import CreateInfo, Reservation
from src.model.reservations.update import Update
from src.model.reservations.reservationQuery import ReservationQuery


class ReservationsProvider:
    
    async def create_reservation(self, reservation: CreateInfo) -> Reservation:
        raise Exception("Interface method should not be called")

    async def update_reservation(self, reservation_id: str, reservation_update: Update) -> Reservation:
        raise Exception("Interface method should not be called")
    
    async def get_reservations(self, query: ReservationQuery) -> List[Reservation]:
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
           return Error.from_exception(e)
    
    async def update_reservation(self, reservation: str, update: Update, response: Response) -> Reservation | Error:
        try:
           return await self.provider.update_reservation(reservation, update)
        except Exception as e:
           response.status_code = status.HTTP_400_BAD_REQUEST
           return Error.from_exception(e)
    
    async def get_reservations(self, query: ReservationQuery, response: Response) -> List[Reservation] | Error:
        try:
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
        response = await post(f"{self.url}{endpoint}", body=reservation.model_dump())
        return await recover_json_data(response) 

    async def update_reservation(self, reservation_id: str, reservation_update: Update) -> Reservation:
        endpoint = "/reservations"
        response = await put(f"{self.url}{endpoint}/{reservation_id}", body=reservation_update.model_dump())
        return await recover_json_data(response) 

    async def get_reservations(self, query: ReservationQuery) -> List[Reservation]:
        endpoint = "/reservations"
        response = await get(f"{self.url}{endpoint}", params=query.model_dump())
        return await recover_json_data(response)

    async def delete_reservation(self, reservation_id: str) -> None:
        endpoint = "/reservations"
        await delete(f"{self.url}{endpoint}/{reservation_id}")
        return  

class LocalReservationsProvider(ReservationsProvider):
    
    def __init__(self, base: ReservationsBase):
        self.db = base

    async def create_reservation(self, reservation: CreateInfo) -> Reservation:
        persistance = reservation.into_reservation().persistance()
        self.db.store_reservation(persistance)
        return Reservation.from_schema(persistance)

    async def update_reservation(self, reservation_id: str, reservation_update: Update) -> Reservation:
        schema = self.db.get_reservation_by_id(reservation_id)
        if schema:
            reservation = Reservation.from_schema(schema)
            reservation = reservation_update.modify(reservation)
            self.db.update_reservation(reservation.persistance())
            return reservation
        raise Exception("Reservation does not exist")

    async def get_reservations(self, query: ReservationQuery) -> List[Reservation]:
        return query.query(self.db)

    async def delete_reservation(self, reservation_id: str) -> None:
        Reservation.delete(reservation_id, self.db)
