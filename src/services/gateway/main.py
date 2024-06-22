from typing import Annotated, List
from fastapi import Body, Depends, FastAPI, Header, Path, Query, Response, status
from pydantic_settings import BaseSettings
from src.model.commons.error import Error
from src.model.gateway import HelloResponse
import requests as r
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from src.model.reservations.reservation import CreateInfo, Reservation
from src.model.reservations.reservationQuery import ReservationQuery
from src.model.reservations.service import HttpReservationsProvider, ReservationsService
from src.model.reservations.update import Update
from src.model.users.service import HttpUsersProvider
from src.model.users.user_data import UserData, UserToken
from src.model.gateway.users_middleware import AuthMiddleware
from src.model.gateway.service import GatewayService


class Settings(BaseSettings):
    proto: str = "http://"
    users: str = "users"
    reservations: str = "reservations"
    auth_url: str = "/users/permissions"
    auth_avoided_urls: list[str] = ["/users"]
    information_prefix: str = "/users"
    dev: bool = True

settings = Settings()
app = FastAPI()

app.add_middleware(AuthMiddleware, 
                   authUrl=f"{settings.proto}{settings.users}{settings.auth_url}", 
                   avoided_urls=settings.auth_avoided_urls,
                   dev_mode=settings.dev)

security = HTTPBearer()
users = HttpUsersProvider(f"{settings.proto}{settings.users}")
reservations = HttpReservationsProvider(f"{settings.proto}{settings.reservations}")
service = GatewayService(users, ReservationsService(reservations))

@app.get("/users/health")
async def users_health(_: Annotated[HTTPAuthorizationCredentials, Depends(security)], 
                                              response: Response):
    users_response = r.get(f"{settings.proto}{settings.users}/health")
    response.status_code = users_response.status_code

@app.get("/users")
async def sign_in(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
                  response: Response) -> UserData | Error:
    return await service.sign_in(credentials, response)

@app.post("/users")
async def sign_up(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
                  user_type: Annotated[str, Body(embed=True, alias='user_type')]) -> UserData | Error:
    
    return await service.sign_up(credentials, user_type)

@app.post("/reservations")
async def create_reservation(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
                             reservation: Annotated[CreateInfo, Body()],
                             response: Response) -> Reservation | Error:
    return await service.create_reservation(reservation, response)

@app.put("/reservations/{reservation_id}")
async def update_reservations(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
                              reservation: Annotated[Update, Body()],
                              reservation_id: Annotated[str, Path()],
                              response: Response
                              ) -> Reservation | Error:
    return await service.update_reservation(reservation_id, reservation, response)

@app.delete("/reservations/{reservation_id}")
async def delete_reservations(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
                              reservation_id: Annotated[str, Path()],
                              response: Response) -> None:
    return await service.delete_reservation(reservation_id, response)

@app.get("/reservations")
async def get_reservations(response: Response,
                           id: str = Query(default=None),
                           user: str = Query(default=None),
                           venue: str = Query(default=None),
                           from_time: str = Query(default=None),
                           to_time: str = Query(default=None),
                           from_people: int = Query(default=None),
                           to_people: int = Query(default=None),
                           ) -> List[Reservation] | Error:
    query = ReservationQuery(
            id=id,
            user=user,
            venue=venue,
            time=(from_time, to_time) if from_time != None and to_time != None else None,
            people=(from_people, to_people) if from_people != None and to_people != None else None
            )
    return await service.get_reservations(query, response)
 
