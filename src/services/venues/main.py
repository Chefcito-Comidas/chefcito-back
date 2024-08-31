from src.model.commons.error import Error
from src.model.venues.venueQuery import VenueQuery, VenueQueryResult
from src.model.venues.update import Update
from typing import Annotated, List, Tuple
from fastapi import Body, FastAPI, Path, Query, Response, status
from pydantic_settings import BaseSettings
from src.model.venues.data.base import MockBase, RelBase
from src.model.venues.venue import CreateInfo, Venue
from src.model.venues.venueQuery import VenueQuery
from src.model.venues.service import LocalVenuesProvider, VenuesProvider, VenuesService
from datetime import datetime


class Settings(BaseSettings):
    db_string: str = "database_conn_string"

settings = Settings()

app = FastAPI()
database =  RelBase(settings.db_string) 
service = VenuesService(LocalVenuesProvider(database))


@app.post("/venues")
async def create_venue(venue: Annotated[CreateInfo, Body()], response: Response) -> Venue | Error:
    return await service.create_venue(venue, response)

@app.put("/venues/{venue}")
async def update_venue(venue: Annotated[str, Path()], update: Annotated[Update, Body()], response: Response) -> Venue | Error:
    print(venue)
    return await service.update_venue(venue, update, response)

@app.delete("/venues/{venue}", responses={status.HTTP_400_BAD_REQUEST: {"model": Error}})
async def delete_venue(venue: Annotated[str, Path()]) -> None:
    return await service.delete_venue(venue)

@app.get("/venues")
async def get_venues(response: Response,
                           id: str = Query(default=None),
                           name: str = Query(default=None),
                           location: str = Query(default=None),
                           capacity: int = Query(default=None),
                           logo: str = Query(default=None),
                           pictures: List[str] = Query(default=None),
                           slots: List[datetime] = Query(default=None),
                           characteristics: List[str] = Query(default=None),
                           vacations: List[datetime] = Query(default=None),
                           reservationLeadTime: int = Query(default=None),
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
            characteristics=characteristics,
            vacations=vacations,
            reservationLeadTime=reservationLeadTime,
            limit=limit,
            start=start
            )
    return await service.get_venues(query, response)

@app.get("venues/near")
async def get_venues_near_to(response: Response,
                             location: Tuple[str, str] = Query(default=("-34.594174","-58.4566507"))
                             ) -> VenueQueryResult | Error:
    return await service.get_venues_near_to(location, response)