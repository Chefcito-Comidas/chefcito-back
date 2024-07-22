from datetime import datetime
from typing import Annotated, List, Optional
from fastapi import Body, Depends, FastAPI, Header, Path, Query, Response, status
from pydantic_settings import BaseSettings
from src.model.commons.error import Error
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from src.model.venues.venue import Venue
from src.model.venues.venueQuery import VenueQuery
from src.model.venues.service import HttpVenuesProvider, VenuesService

from src.model.reservations.reservation import Reservation
from src.model.reservations.service import HttpReservationsProvider, ReservationsService
from src.model.users.service import HttpUsersProvider
from src.model.users.user_data import UserData
from src.model.gateway.users_middleware import AuthMiddleware
from src.model.gateway.service import GatewayService
from src.model.gateway.reservations_stubs import CreateInfo, Update, ReservationQuery
import src.model.venues as v
import src.model.gateway.venues_stubs as v_stubs

class Settings(BaseSettings):
    proto: str = "http://"
    users: str = "users"
    venues: str = "venues"
    reservations: str = "reservations"
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
service = GatewayService(users, ReservationsService(reservations),VenuesService(venues))

@app.get("/users", responses={status.HTTP_400_BAD_REQUEST: {"model": Error}})
async def sign_in(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
                  response: Response) -> UserData | Error:
    return await service.sign_in(credentials, response)

@app.post("/users", responses={status.HTTP_400_BAD_REQUEST: {"model": Error}})
async def sign_up(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
                  user_type: Annotated[str, Body(embed=True, alias='user_type')]) -> UserData | Error:
    
    return await service.sign_up(credentials, user_type)


@app.post("/venues", response_model=Venue)
async def create_venue(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
                             venue: Annotated[v_stubs.CreateInfo, Body()],
                             response: Response) -> Venue | Error:
    answer = await service.create_venue(credentials, venue, response)
    print(f"Created: {answer}")
    return answer

@app.put("/venues/{venue_id}",response_model=Venue)
async def update_venues(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
                              venue: Annotated[v.update.Update, Body()],
                              venue_id: Annotated[str, Path()],
                              response: Response
                              ) -> Venue:
    
    answer = await service.update_venue(credentials,venue_id, venue, response)
    print(f"Answering: {answer}")
    return answer

@app.delete("/venues/{venue_id}")
async def delete_venues(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
                              venue_id: Annotated[str, Path()],
                              response: Response) -> None:
    return await service.delete_venue(venue_id, response)

@app.get("/venues")
async def get_venues(response: Response,
                           id: str = Query(default=None),
                           name: str = Query(default=None),
                           location: str = Query(default=None),
                           capacity: int = Query(default=None),
                           logo: str = Query(default=None),
                           pictures: List[str] = Query(default=None),
                           slots: List[datetime] = Query(default=None),
                           limit: int = Query(default=10),
                           start: int = Query(default=0)
                           ) -> List[Venue] | Error:
    query = VenueQuery(
            id=id,
            name=name,
            location=location,
            capacity=capacity,
            logo=logo,
            pictures=pictures,
            slots=slots,
            limit=limit,
            start=start
            )
    return await service.get_venues(query, response)
  
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
                           status: Optional[str] = Query(default=None),
                           venue: Optional[str] = Query(default=None),
                           from_time: Optional[datetime] = Query(default=None),
                           to_time: Optional[datetime] = Query(default=None),
                           from_people: Optional[int] = Query(default=None),
                           to_people: Optional[int] = Query(default=None),
                           limit: int = Query(default=10),
                           start: int = Query(default=0)
                           ) -> List[Reservation] | Error:
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
 
