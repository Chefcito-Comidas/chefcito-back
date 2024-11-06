from datetime import datetime
from re import S
from typing import Annotated, List, Optional, Tuple
from fastapi import Body, Depends, FastAPI, Header, Path, Query, Response, status
from pydantic_settings import BaseSettings
from src.model.commons.error import Error
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from src.model.opinions.opinion import Opinion
from src.model.opinions.opinion_query import OpinionQuery, OpinionQueryResponse
from src.model.points.provider import HttpPointsProvider
from src.model.reservations.reservationQuery import ReservationQueryResponse
from src.model.stats.user_data import UserStatData
from src.model.stats.venue_data import VenueStatData
from src.model.summarizer.summary import Summary
from src.model.users.update import UserUpdate
from src.model.venues.venue import Venue
from src.model.venues.venueQuery import VenueDistanceQueryResult, VenueQuery, VenueQueryResult
from src.model.venues.service import HttpVenuesProvider, VenuesService

from src.model.reservations.reservation import Reservation
from src.model.reservations.service import HttpReservationsProvider, ReservationsService
from src.model.users.service import HttpUsersProvider
from src.model.users.user_data import UserData
from src.model.gateway.users_middleware import AuthMiddleware
from src.model.gateway.service import GatewayService
from src.model.gateway.reservations_stubs import CreateInfo, Update, ReservationQuery
import src.model.venues as v
from src.model.venues.update import Update as VUpdate
import src.model.gateway.venues_stubs as v_stubs
import src.model.gateway.users_stubs as u_stubs

class Settings(BaseSettings):
    proto: str = "http://"
    users: str = "users"
    venues: str = "venues"
    reservations: str = "reservations"
    points: str = "points"
    auth_url: str = "/users/permissions"
    auth_avoided_urls: list[str] = ["/users"]
    information_prefix: str = "/users"
    dev: bool = True

settings = Settings()
app = FastAPI()

app.add_middleware(CORSMiddleware,
                   allow_origins=["*"],
                   allow_credentials=True,
                   allow_methods=["*"],
                   allow_headers=["*"])

app.add_middleware(AuthMiddleware,
                   authUrl=f"{settings.proto}{settings.users}{settings.auth_url}",
                   avoided_urls=settings.auth_avoided_urls,
                   dev_mode=settings.dev)

security = HTTPBearer()
users = HttpUsersProvider(f"{settings.proto}{settings.users}")
venues = HttpVenuesProvider(f"{settings.proto}{settings.venues}")
reservations = HttpReservationsProvider(f"{settings.proto}{settings.reservations}")
points = HttpPointsProvider(f"{settings.proto}{settings.points}")
service = GatewayService(users, ReservationsService(reservations),VenuesService(venues), points)

@app.get("/users", responses={status.HTTP_400_BAD_REQUEST: {"model": Error}})
async def sign_in(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
                  response: Response) -> u_stubs.UserData | Error:
    return await service.sign_in(credentials, response)

@app.post("/users", responses={status.HTTP_400_BAD_REQUEST: {"model": Error}})
async def sign_up(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
                  user_type: Annotated[str, Body(embed=True, alias='user_type')],
                  name: Annotated[str, Body(embed=True, alias='name')],
                  number: Annotated[str, Body(embed=True, alias="number")]) -> UserData | Error:
    return await service.sign_up(credentials, user_type, name, number)

@app.put("/users")
async def update_data(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
                      update: Annotated[UserUpdate, Body()]) -> u_stubs.UserData:
    return await service.update(credentials, update)

@app.post("/venues",responses={status.HTTP_400_BAD_REQUEST: {"model": Error},
                                         status.HTTP_200_OK: {"model": Venue}})
async def create_venue(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
                             venue: Annotated[v_stubs.CreateInfo, Body()],
                             response: Response) -> Venue | Error:
    answer = await service.create_venue(credentials, venue, response)
    print(f"Created: {answer}")
    return answer

@app.put("/venues/{venue_id}",responses={status.HTTP_400_BAD_REQUEST: {"model": Error},
                                         status.HTTP_200_OK: {"model": Venue}})
async def update_venues(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
                              venue: Annotated[VUpdate, Body()],
                              venue_id: Annotated[str, Path()],
                              response: Response
                              ) -> Venue | Error:

    answer = await service.update_venue(credentials,venue_id, venue, response)
    return answer

@app.delete("/venues/{venue_id}")
async def delete_venues(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
                              venue_id: Annotated[str, Path()],
                              response: Response) -> None:
    return await service.delete_venue(credentials, venue_id, response)

@app.get("/venues")
async def get_venues(response: Response,
                           id: str = Query(default=None),
                           name: str = Query(default=None),
                           location: str = Query(default=None),
                           capacity: int = Query(default=None),
                           logo: str = Query(default=None),
                           pictures: List[str] = Query(default=None),
                           slots: List[datetime] = Query(default=None),
                           characteristic: List[str] = Query(default=None),
                           feature: List[str] = Query(default=None),
                           vacations: List[datetime] = Query(default=None),
                           reservationLeadTime: int = Query(default=None),
                           menu: str = Query(default=None),
                           limit: int = Query(default=10),
                           start: int = Query(default=0)
                           ) -> VenueQueryResult | Error:
    query = VenueQuery(
            id=id,
            name=name,
            location=location,
            capacity=capacity,
            logo=logo,
            pictures=pictures,
            slots=slots,
            characteristics=characteristic,
            features=feature,
            vacations=vacations,
            reservationLeadTime=reservationLeadTime,
            menu=menu,
            limit=limit,
            start=start
            )
    return await service.get_venues(query, response)

@app.get("/venues/near")
async def get_venues_near_to(response: Response,
                             credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
                             location: Tuple[str, str] = Query(default=("-34.594174","-58.4566507")),
                             ) -> VenueDistanceQueryResult | Error:
    return await service.get_venues_near_to(location, response)

@app.post("/reservations", responses={status.HTTP_400_BAD_REQUEST: {"model": Error}})
async def create_reservation(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
                             reservation: Annotated[CreateInfo, Body()],
                             response: Response) -> Reservation | Error:
    result = await service.create_reservation(credentials, reservation, response)
    return result
@app.put("/reservations/{reservation_id}", responses={status.HTTP_400_BAD_REQUEST: {"model": Error}})
async def update_reservations(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
                              reservation: Annotated[Update, Body()],
                              reservation_id: Annotated[str, Path()],
                              response: Response
                              ) -> Reservation | Error:
    return await service.update_reservation(credentials, reservation_id, reservation, response)

@app.delete("/reservations/{reservation_id}", responses={status.HTTP_400_BAD_REQUEST: {"model": Error}})
async def delete_reservations(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
                              reservation_id: Annotated[str, Path()],
                              response: Response) -> None:
    return await service.delete_reservation(credentials, reservation_id, response)

@app.get("/reservations", responses={status.HTTP_400_BAD_REQUEST: {"model": Error}})
async def get_reservations(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
                           response: Response,
                           id: Optional[str] = Query(default=None),
                           status: Optional[List[str]] = Query(default=None),
                           venue: Optional[str] = Query(default=None),
                           from_time: Optional[datetime] = Query(default=None),
                           to_time: Optional[datetime] = Query(default=None),
                           from_people: Optional[int] = Query(default=None),
                           to_people: Optional[int] = Query(default=None),
                           limit: int = Query(default=10),
                           start: int = Query(default=0)
                           ) -> ReservationQueryResponse | Error:
    query = ReservationQuery(
            id=id,
            venue=venue,
            status=status,
            from_time=from_time,
            to_time=to_time,
            people=(from_people, to_people) if from_people != None and to_people != None else None,
            limit=limit,
            start=start
            )
    return await service.get_reservations(credentials, query, response)


@app.get("/reservations/history", responses={status.HTTP_400_BAD_REQUEST: {"model": Error}})
async def get_history(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
                      response: Response,
                      from_time: Optional[datetime] = Query(default=None),
                      to_time: Optional[datetime] = Query(default=None),
                      limit: int = Query(default=10),
                      start: int = Query(default=0)) -> ReservationQueryResponse | Error:
    return await service.get_history(credentials, from_time, to_time, limit, start, False, response)

@app.get("/reservations/venue", responses={status.HTTP_400_BAD_REQUEST: {"model": Error}})
async def get_venue_history(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
                            response: Response,
                            from_time: Optional[datetime] = Query(default=None),
                            to_time: Optional[datetime] = Query(default=None),
                            limit: int = Query(default=10),
                            start: int = Query(default=0)) -> ReservationQueryResponse | Error:
    return await service.get_history(credentials, from_time, to_time, limit, start, True, response)

@app.get("/opinions", responses={status.HTTP_400_BAD_REQUEST: {"model": Error}})
async def query_opinions(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
                         response: Response,
                         venue: Optional[str] = Query(default=None),
                         from_date: Optional[datetime] = Query(default=None),
                         to_date: Optional[datetime] = Query(default=None),
                         limit: int = Query(default=10),
                         start: int = Query(default=0)) -> OpinionQueryResponse | Error:
    query = OpinionQuery(
        venue=venue,
        from_date=from_date,
        to_date=to_date,
        limit=limit,
        start=start
    )

    return await service.get_opinions(query, response)

@app.post("/opinions", responses={status.HTTP_400_BAD_REQUEST: {"model": Error}})
async def create_opinion(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)], opinion: Opinion, response: Response) -> Opinion | Error:
    return await service.create_opinion(credentials, opinion, response)


@app.get("/venue", responses={
    status.HTTP_400_BAD_REQUEST: {"model": Error},
    status.HTTP_200_OK: {"model": Venue}
    })
async def get_venue_info(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
                         response: Response) -> Venue | Error:
    return await service.get_my_venue(credentials, response)


@app.post("/summaries/{venue}", responses={status.HTTP_400_BAD_REQUEST: {"model": Error}})
async def create_venue_summary(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
                               venue: Annotated[str, Path()]) -> Summary:
    return await service.create_venue_summary(venue, credentials)

@app.get("/summaries/{venue}", responses={status.HTTP_400_BAD_REQUEST: {"model": Error}})
async def get_venue_summary(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
                            venue: Annotated[str, Path()]) -> Summary:
    return await service.get_venue_summary(venue)

@app.get("/stats/user/{user}")
async def get_user_stats(user: str, credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]) -> UserStatData:
    return await service.get_user_stats(user)

@app.get("/stats/venue/{venue}")
async def get_venue_stats(venue: str, credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)]) -> VenueStatData:
    return await service.get_venue_stats(venue)


@app.get("/venues/promotions")
async def get_promoted_venues() -> VenueQueryResult:
    """
    Returns Some mocked results based on a couple Queries
    """
    return await service.get_promotions()
