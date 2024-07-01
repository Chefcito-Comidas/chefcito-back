from typing import List
from src.model.venues.data.base import MockBase  
from src.model.venues.data.schema import VenueSchema 
from src.model.venues.venueQuery import VenueQuery
from src.model.venues.venue import Venue, Available

def create_venues(amount: int) -> List[VenueSchema]:
    """
    Crea una lista de venues con IDs incrementales y ubicaciones alternas.
    """
    venues = []
    for i in range(amount):
        venues.append(VenueSchema(
            id=f"{i}",
            name=f"Venue {i}",
            location=f"Location {i % 2}",
            capacity=f"{i%5}",
            status=Available().get_status()
        ))
    return venues

def all_same_name(name: str, result: List[VenueSchema]) -> bool:
    """
    Verifica si todos los venues en el resultado tienen el mismo nombre.
    """
    for venue in result:
        if venue.name != name:
            return False
    return True

def all_same_location(location: str, result: List[VenueSchema]) -> bool:
    """
    Verifica si todos los venues en el resultado tienen la misma ubicación.
    """
    for venue in result:
        if venue.location != location:
            return False
    return True

def test_get_all_by_same_name():
    """
    Prueba para obtener todos los venues con el mismo nombre.
    """
    database = MockBase()
    for venue in create_venues(9):
        database.store_venue(venue)
    query = VenueQuery(
        name="Venue 5"  
    )
    result = query.query(database)
    assert len(result) == 1  
    assert all_same_name("Venue 5", result)

# TODO: TODAVIA NO IMPLEMENTADO por location o por status
# def test_get_all_by_same_location():
#     """
#     Prueba para obtener todos los venues con la misma ubicación.
#     """
#     database = MockBase()
#     for venue in create_venues(9):
#         database.store_venue(venue)
#     query = VenueQuery(
#         location="Location 1"  
#     )
#     result = query.query(database)
#     assert len(result) == 5  
#     assert all_same_location("Location 1", result)
