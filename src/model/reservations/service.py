from datetime import datetime
from logging import log
import logging
from typing import List
from fastapi import HTTPException, Response, status

from src.model.commons.caller import delete, get, post, put, recover_json_data
from src.model.commons.error import Error
from src.model.communications.message import Message
from src.model.communications.service import CommunicationProvider, DummyCommunicationProvider
from src.model.opinions.opinion import Opinion
from src.model.opinions.opinion_query import OpinionQuery, OpinionQueryResponse
from src.model.opinions.provider import OpinionsProvider
from src.model.reservations.data.base import ReservationsBase
from src.model.reservations.data.schema import ReservationSchema
from src.model.reservations.reservation import CreateInfo, Reservation, ReservationStatus
from src.model.reservations.update import Update
from src.model.reservations.reservationQuery import ReservationQuery, ReservationQueryResponse
from src.model.stats.provider import StatsProvider
from src.model.stats.user_data import UserStatData
from src.model.stats.venue_data import VenueStatData
from src.model.summarizer.summary import Summary
from src.model.venues.service import VenuesProvider
from src.model.venues.venueQuery import VenueQuery, VenueQueryResult
from src.model.commons.logger import Logger, define_log_level

class ReservationsProvider:
    
    async def create_reservation(self, reservation: CreateInfo) -> Reservation:
        raise Exception("Interface method should not be called")

    async def update_reservation(self, reservation_id: str, reservation_update: Update) -> Reservation:
        raise Exception("Interface method should not be called")
    
    async def get_reservations(self, query: ReservationQuery) -> ReservationQueryResponse:
        raise Exception("Interface method should not be called")
    
    async def delete_reservation(self, reservation_id: str) -> None:
        raise Exception("Interface method should not be called")

    async def create_opinion(self, opinion: Opinion, user: str) -> Opinion:
        raise Exception("Interface method should not be called")

    async def get_opinions(self, query: OpinionQuery) -> OpinionQueryResponse:
        raise Exception("Interface method should not be called")

    async def get_venue_stats(self, venue: str) -> VenueStatData:
        raise Exception("Interface mehotd should not be called")
    
    async def get_user_stats(self, user: str) -> UserStatData:
        raise Exception("Interface method should not be called")
    
    async def get_venue_summary(self, venue: str) -> Summary:
        raise Exception("Interface method should not be called")

    async def  create_venue_summary(self, venue: str) -> Summary:
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
           return await self.provider.get_reservations(query)
        except Exception as e:
           response.status_code = status.HTTP_400_BAD_REQUEST
           return Error.from_exception(e)
    
    async def delete_reservation(self, reservation_id: str) -> None:
        try:
            await self.provider.delete_reservation(reservation_id)
        finally:
            return

    async def create_opinion(self, opinion: Opinion, user: str, response: Response) -> Opinion | Error:
        try:
            return await self.provider.create_opinion(opinion, user)
        except Exception as e:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return Error.from_exception(e)
    
    async def get_opinions(self, query: OpinionQuery, response: Response) -> OpinionQueryResponse | Error:
        try:
            return await self.provider.get_opinions(query)
        except Exception as e:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return Error.from_exception(e)


    async def get_user_stats(self, user: str) -> UserStatData:
        try:
            return await self.provider.get_user_stats(user)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=e.__str__()
            )

    async def get_venue_stats(self, venue: str) -> VenueStatData:
        try:
            return await self.provider.get_venue_stats(venue)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=e.__str__()
            )
        
    async def get_venue_summary(self, venue: str) -> Summary:
        try:
            return await self.provider.get_venue_summary(venue)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=e.__str__()
            )
        
    async def create_venue_summary(self, venue: str) -> Summary:
        try:
            return await self.provider.create_venue_summary(venue)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=e.__str__()
            )

class HttpReservationsProvider(ReservationsProvider):
    def __init__(self, service_url: str):
        self.url = service_url

    async def create_reservation(self, reservation: CreateInfo) -> Reservation:
        endpoint = "/reservations"
        body = reservation.model_dump()
        body['time'] = body['time'].__str__()
        Logger.info(f"Sending create reservation request with data: {body}")
        response = await post(f"{self.url}{endpoint}", body=body)
        data = await recover_json_data(response) 
        data['time'] = datetime.fromisoformat(data['time'])
        return data

    async def update_reservation(self, reservation_id: str, reservation_update: Update) -> Reservation:
        endpoint = "/reservations"
        body = reservation_update.model_dump(exclude_none=True)
        if body.get('time'):
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

    async def create_opinion(self, opinion: Opinion, user: str) -> Opinion:
        endpoint = "/opinions"
        response = await post(f"{self.url}{endpoint}/{user}", body=opinion.model_dump())
        return await recover_json_data(response)

    async def get_opinions(self, query: OpinionQuery) -> List[Opinion]:
        endpoint = "/opinions"
        params = query.model_dump(exclude_none=True)
        if params.get("from_time"):
            params["from_time"] = params["from_time"].__str__()
        if params.get("to_time"):
            params["to_time"] = params["to_time"].__str__()
        response = await get(f"{self.url}{endpoint}", params=params)
        return await recover_json_data(response)

    async def get_user_stats(self, user: str) -> UserStatData:
        endpoint = f"/stats/user/{user}"
        response = await get(f"{self.url}{endpoint}")
        return await recover_json_data(response)
    
    async def get_venue_stats(self, venue: str) -> VenueStatData:
        endpoint = f"/stats/venue/{venue}"
        response = await get(f"{self.url}{endpoint}")
        return await recover_json_data(response)

    async def get_venue_summary(self, venue: str) -> Summary:
        endpoint = f"/summaries/{venue}"
        response = await get(f"{self.url}{endpoint}")
        return await recover_json_data(response)
    
    async def create_venue_summary(self, venue: str) -> Summary:
        endpoint = f"/summaries/{venue}"
        response = await post(f"{self.url}{endpoint}")
        return await recover_json_data(response)

class LocalReservationsProvider(ReservationsProvider):
    
    def __init__(self, base: ReservationsBase, venues: VenuesProvider, opinions: OpinionsProvider,
                 stats: StatsProvider, 
                 comms: CommunicationProvider = DummyCommunicationProvider()):
        self.db = base
        self.venues = venues
        self.opinions = opinions
        self.communications = comms
        self.stats = stats

    async def __notify_user(self, user: str, message: str) -> None:
        to_send = Message(user=user, message=message)
        try:
            await self.communications.send_message(to_send)
        except Exception as e:
            logging.error(f"Could not send message to: {user} ({e})")

    async def _find_venue(self, venue_id: str) -> bool:
        query = VenueQuery(id=venue_id)
        result = await self.venues.get_venues(query)
        if isinstance(result, dict):
            return result['total'] != 0
        return result.total != 0 # type: ignore

    async def __notify_state_change(self, to: str, venue_id: str, new_state: ReservationStatus):
        venue = await self.venues.get_venues(VenueQuery(id=venue_id))
        try:
            if isinstance(venue, dict):
                name = venue['result'].pop()['name']
            else:
                name = venue.result.pop().name
                
            message = f"Tienes un cambio de estado en tu reserva en {name}!\n{new_state.status_message()}"
            await self.communications.send_message(Message(user=to, message=message)) 
        except Exception as e:
            logging.error(f"Could not send message update to venue")
            
    async def create_reservation(self, reservation: CreateInfo) -> Reservation:
        Logger.info(f"New reservation: {reservation}")
        if not await self._find_venue(reservation.venue):
            Logger.info("Tried to created a reservation for an unexisting venue")
            raise Exception("Venue does not exist")
        Logger.info(f"Creating new reservation for: {reservation.user}")
        persistance = reservation.into_reservation().persistance()
        Logger.info("=Persisted reservation schema created")
        response = Reservation.from_schema(persistance)
        self.db.store_reservation(persistance)
        Logger.info("=Stored reservation in database")
        await self.__notify_user(
            reservation.user,
            message=f"Tu reserva para el dia {response.time.date()} fue creada con exito!"
        )
        Logger.info("=Sent notification to user")
        await self.__notify_user(
            reservation.venue,
            message=f"Crearon una nueva reserva para el dia {response.time.date()}, podes verla agregada en la web!"
        )
        Logger.info("=Sent notification to venue") 
        return response 

    async def update_reservation(self, reservation_id: str, reservation_update: Update) -> Reservation:
        Logger.info(f"Update request for reservation: {Update}")
        schema = self.db.get_reservation_by_id(reservation_id)
        if schema:
            Logger.info("Updating reservation from schema")
            reservation = Reservation.from_schema(schema)
            reservation = await reservation_update.modify(reservation, self.stats)
            Logger.info(f"Modified reservation: {reservation}")
            self.db.update_reservation(reservation.persistance())
            Logger.info("Persisted reservation")
            await self.__notify_user(
                reservation.venue,
                message=f"Tienes una modeficacion en la reserva ({reservation.id}): del dia {schema.time.date()}!\nPodes ver las modificaciones de la reserva en la web"
            )
            await self.__notify_state_change(reservation.user, reservation.venue, reservation.status)
            Logger.info("Notifications sent")
            return reservation
        raise Exception("Reservation does not exist")

    async def get_reservations(self, query: ReservationQuery) -> ReservationQueryResponse:
        Logger.info(f"Reservation query recieved: {query}")
        return await query.query(self.db, self.opinions)

    async def delete_reservation(self, reservation_id: str) -> None:
        Logger.info(f"Reservation deletion for reservation id: {reservation_id}")
        Reservation.delete(reservation_id, self.db)

    async def create_opinion(self, opinion: Opinion, user: str) -> Opinion:
        Logger.info(f"Opinion creation for reservation {opinion.reservation}")
        query = ReservationQuery(
            id=opinion.reservation
        )
        result = await self.get_reservations(query)
        if result.total == 0 and user not in result.result[0].user:
            raise Exception("Reservation was not done by user")
        Logger.info("Creating opinion")
        created_opinion = await self.opinions.create_opinion(opinion)
        await self.__notify_user(result.result[0].venue,
                           message="Tenes una nueva opinion en tu local!\nPodes revisarla en nuestra web")
        Logger.info("Opinion created and venue notified of new opinion")
        return created_opinion

    async def get_opinions(self, query: OpinionQuery) -> OpinionQueryResponse:
        Logger.info(f"Recieved opinion query request {query}")
        return await self.opinions.query_opinions(query)

    async def get_user_stats(self, user: str) -> UserStatData:
        Logger.info(f"Recieved request for user => {user} stats")
        return await self.stats.get_user(user)
    
    async def get_venue_stats(self, venue: str) -> VenueStatData:
        Logger.info(f"Recieved request for venue ==> {venue} stats")
        return await self.stats.get_venue(venue)

    async def get_venue_summary(self, venue: str) -> Summary:
        Logger.info(f"Recovering venue ==> {venue} summary")
        return await self.opinions.get_venue_summary(venue)
    
    async def create_venue_summary(self, venue: str) -> Summary:
        Logger.info(f"Creating venue ==> {venue} Summary")
        return await self.opinions.create_venue_summary(venue)