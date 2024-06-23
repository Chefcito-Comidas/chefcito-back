from typing import Annotated, List
from fastapi import Body, FastAPI, Response

from src.model.commons.error import Error
from src.model.venues.venue import Venue
from src.model.venues.venueQuery import VenueQuery
from src.model.venues.service import VenuesProvider, VenuesService
from src.model.venues.update import Update


app = FastAPI()
service = VenuesService(VenuesProvider())


@app.post("/venue")
async def create_venue(venue: Annotated[Venue, Body()], response: Response) -> Venue | Error:
    return await service.create_venue(venue, response)

@app.put("/venue")
async def update_venue(venue: Annotated[Venue, Body()], update: Annotated[Update, Body()], response: Response) -> Venue | Error:
    return await service.update_venue(venue, update, response)

@app.post("/search")
async def get_venues(query: Annotated[VenueQuery, Body()], response: Response) -> List[Venue] | Error:
    # TODO: add pagination to this particular endpoint
    return await service.get_venues(query, response)
