from src.model.commons.error import Error
from src.model.venues.venueQuery import VenueQuery
from src.model.venues.update import Update
from typing import Annotated, List, Tuple
from fastapi import Body, FastAPI, Path, Query, Response
from pydantic_settings import BaseSettings
from src.model.venues.data.base import MockBase, RelBase
from src.model.venues.venue import CreateInfo, Venue
from src.model.venues.venueQuery import VenueQuery
from src.model.venues.service import LocalVenuesProvider, VenuesProvider, VenuesService



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


@app.get("/venues/")
async def get_venues(response: Response,
                           id: str = Query(default=None),
                           name: str = Query(default=None),
                           location: str = Query(default=None),
                           capacity: int = Query(default=None),
                           ) -> List[Venue] | Error:
    print("Here I Am")
    query = VenueQuery(
            id=id,
            name=name,
            location=location,
            capacity=capacity
            )
    return await service.get_venues(query, response)