from datetime import datetime
from typing import Annotated, List
from fastapi import Body, Depends, FastAPI, Header, Path, Query, Response, status
from pydantic_settings import BaseSettings
from src.model.commons.error import Error
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from src.model.venues.venue import CreateInfo, Venue
from src.model.venues.venueQuery import VenueQuery
from src.model.venues.service import HttpVenuesProvider, VenuesService
from src.model.venues.update import Update
from src.model.reservations.reservation import Reservation
from src.model.reservations.service import HttpReservationsProvider, ReservationsService
from src.model.users.service import HttpUsersProvider
from src.model.users.user_data import UserData, UserToken
from src.model.gateway.users_middleware import AuthMiddleware
from src.model.gateway.service import GatewayService
from src.model.gateway.reservations_stubs import CreateInfo, Update, ReservationQuery

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

@app.get("/users")
async def sign_in(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
                  response: Response) -> UserData | Error:
    return await service.sign_in(credentials, response)

@app.post("/users")
async def sign_up(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
                  user_type: Annotated[str, Body(embed=True, alias='user_type')]) -> UserData | Error:
    
    return await service.sign_up(credentials, user_type)

@app.post("/venues")
async def create_venue(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
                             venue: Annotated[CreateInfo, Body()],
                             response: Response) -> Venue | Error:
    return await service.create_venue(venue, response)

@app.put("/venues/{venue_id}")
async def update_venues(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
                              venue: Annotated[Update, Body()],
                              venue_id: Annotated[str, Path()],
                              response: Response
                              ) -> Venue | Error:
    return await service.update_venue(venue_id, venue, response)

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
                           limit: int = Query(default=10),
                           start: int = Query(default=0)
                           ) -> List[Venue] | Error:
    query = VenueQuery(
            id=id,
            name=name,
            location=location,
            capacity=capacity,
            limit=limit,
            start=start
            )
    return await service.get_venues(query, response)
@app.post("/reservations")
async def create_reservation(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
                             reservation: Annotated[CreateInfo, Body()],
                             response: Response) -> Reservation | Error:
    return await service.create_reservation(credentials, reservation, response)

@app.put("/reservations/{reservation_id}")
async def update_reservations(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
                              reservation: Annotated[Update, Body()],
                              reservation_id: Annotated[str, Path()],
                              response: Response
                              ) -> Reservation | Error:
    return await service.update_reservation(credentials, reservation_id, reservation, response)

@app.delete("/reservations/{reservation_id}")
async def delete_reservations(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
                              reservation_id: Annotated[str, Path()],
                              response: Response) -> None:
    return await service.delete_reservation(credentials, reservation_id, response)

@app.get("/reservations")
async def get_reservations(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
                           response: Response,
                           id: str = Query(default=None),
                           status: str = Query(default=None),
                           venue: str = Query(default=None),
                           from_time: datetime = Query(default=None),
                           to_time: datetime = Query(default=None),
                           from_people: int = Query(default=None),
                           to_people: int = Query(default=None),
                           limit: int = Query(default=10),
                           start: int = Query(default=0)
                           ) -> List[Reservation] | Error:
    query = ReservationQuery(
            id=id,
            venue=venue,
            status=status,
            time=(from_time, to_time) if from_time != None and to_time != None else None,
            people=(from_people, to_people) if from_people != None and to_people != None else None,
            limit=limit,
            start=start
            )
    return await service.get_reservations(credentials, query, response)
 
