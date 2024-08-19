from typing import List
from src.model.venues.data.base import MockBase  
from src.model.venues.data.schema import VenueSchema 
from src.model.venues.venueQuery import VenueQuery
from src.model.venues.venue import Venue, Available
from datetime import datetime

def create_venues(amount: int) -> List[VenueSchema]:
    """
    Crea una lista de venues con IDs incrementales y ubicaciones alternas.
    """
    venues = []
    for i in range(amount):
        venues.append(VenueSchema(
            id=f"{i}",
            name=f"name_{i%3}",
            location=f"location_{i % 2}",
            capacity=f"{i%5}",
            logo=f"logo_{i}.png",
            pictures=[f"picture_{i}_1.jpg", f"picture_{i}_2.jpg"],
            slots=[datetime(year=2024, month=i%12 + 1, day=i%28 + 1)],
            characteristics=[f"charact{i}_1", f"charact{i}_2"],
            vacations=[datetime(year=2024, month=i%12 + 1, day=i%28 + 1)],
            reservationLeadTime=f"{i%5}",
            status=Available().get_status()
        ))
    return venues

def all_different(list_1: List[Venue], list_2: List[Venue]) -> bool:
    return not any(
            map(
                lambda x: x in list_2,
                list_1
            )
        )

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
        name="name_1"  
    )
    result = query.query(database)
    assert len(result) == 3  #should be 3
    assert all_same_name("name_1", result)

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


def test_limiting_the_amount_of_venues():
    database = MockBase()
    for venue in create_venues(9):
        database.store_venue(venue)
    query = VenueQuery(
            name="name_1",
            limit=2
            )
    result = query.query(database)
    assert len(result) == 2
    # assert all_same_venue("venue_1", result)

def test_stepping_with_limit_the_amount_of_venues():
    database = MockBase()
    for venue in create_venues(9):
        database.store_venue(venue)
    query = VenueQuery(
            name="name_1",
            limit=2
            )
    result_1 = query.query(database)
    query.start = 2
    result_2 = query.query(database)
    assert len(result_1) == 2
    assert len(result_2) == 1
    assert all_different(result_1, result_2)