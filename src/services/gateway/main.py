from typing import Annotated, List
from fastapi import Body, Depends, FastAPI, Header, Path, Query, Response, status
from pydantic_settings import BaseSettings
from src.model.commons.error import Error
from src.model.gateway import HelloResponse
import requests as r
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from src.model.venues.venue import CreateInfo, Venue
from src.model.venues.venueQuery import VenueQuery
from src.model.venues.service import HttpVenuesProvider, VenuesService
from src.model.venues.update import Update
from src.model.users.service import HttpUsersProvider
from src.model.users.user_data import UserData, UserToken
from src.model.gateway.users_middleware import AuthMiddleware
from src.model.gateway.service import GatewayService


class Settings(BaseSettings):
    proto: str = "http://"
    users: str = "users"
    venues: str = "venues"
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
venues = HttpVenuesProvider(f"{settings.proto}{settings.venues}")
service = GatewayService(users, VenuesService(venues))


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