import asyncio
from random import shuffle
from typing import List
import pytest
from src.model.commons.distance import LocalPosition
from src.model.venues.data.location_finder import Ranker
from src.model.venues.venue import create_venue, Available, Closed, Unconfirmed, Occupied, Venue
from src.model.venues.update import Update
from src.model.venues.data.base import MockBase
from datetime import datetime

def test_new_venue_is_open():
    venue = create_venue("La Pizzeria","125 Main St", 50, logo="foto.url", pictures = ["foto1", "foto2"], slots=[datetime.now(),datetime.now()], characteristics= ["Arepas", "Cafeteria"], features= ["Estacionamiento"], vacations=[datetime.now()], reservationLeadTime=10,menu="comidas.url")
    assert venue.get_status() == Available().get_status()

def test_closing_a_venue_changes_status_to_closed():
    venue = create_venue(name="La Pizzeria", location="123 Main St", capacity=50, logo="foto.url", pictures = ["foto1", "foto2"], slots=[datetime.now()], characteristics= ["Arepas", "Cafeteria"], features= ["Estacionamiento"], vacations=[datetime.now()], reservationLeadTime=10,menu="comidas.url")
    venue.close()
    assert venue.get_status() == Closed().get_status()

def test_opening_a_closed_venue_changes_status_to_open():
    venue = create_venue(name="La Pizzeria", location="123 Main St", capacity=50, logo="foto.url", pictures = ["foto1", "foto2"], slots=[datetime.now()], characteristics= ["Arepas", "Cafeteria"], features= ["Estacionamiento"], vacations=[datetime.now()], reservationLeadTime=10,menu="comidas.url")
    venue.close()
    venue.open()
    assert venue.get_status() == Available().get_status()

def test_updating_a_venue_changes_its_attributes():
    venue = create_venue(name="La Pizzeria", location="123 Main St", capacity=50, logo="foto.url", pictures = ["foto1", "foto2"], slots=[datetime.now()], characteristics= ["Arepas", "Cafeteria"], features= ["Estacionamiento"], vacations=[datetime.now()], reservationLeadTime=10,menu="comidas.url")
    update = Update(name="La Trattoria", location="456 Main St", capacity=60, logo="nuevafoto.url", pictures = ["foto3", "foto4"], slots=[datetime.now(),datetime.now()], characteristics= ["Carnes", "Comida Armenia"], features= ["Wifi"], vacations=[datetime.now(),datetime.now()], reservationLeadTime=20,menu="comidas2.url")
    updated_venue = update.modify(venue)
    assert updated_venue.name == "La Trattoria"
    assert updated_venue.location == "456 Main St"
    assert updated_venue.capacity == 60
    assert updated_venue.logo == "nuevafoto.url"
    assert updated_venue.pictures == ["foto3", "foto4"]
    assert updated_venue.characteristics == ["Carnes", "Comida Armenia"]
    assert updated_venue.features == ["Wifi"]
    assert updated_venue.reservationLeadTime == 20
    assert updated_venue.menu =="comidas2.url"
    assert len(updated_venue.vacations) == 2
    assert len(updated_venue.slots) == 2
    assert updated_venue.get_status() == Unconfirmed().get_status()  # Asumiendo que el estado cambia a Uncomfirmed tras la modificación

def test_occupying_a_venue_changes_status_to_occupied():
    venue = create_venue(name="La Pizzeria", location="123 Main St", capacity=50, logo="foto.url", pictures = ["foto1", "foto2"], slots=[datetime.now()], characteristics= ["Arepas", "Cafeteria"], features= ["Estacionamiento"],vacations=[datetime.now()], reservationLeadTime=10,menu="comidas.url")
    update = Update(occupy=True)
    updated_venue = update.modify(venue)
    assert updated_venue.get_status() == Occupied().get_status()

def test_the_venue_can_close_through_an_update():
    venue = create_venue("La Pizzeria", "123 Main St", 50, logo="foto.url", pictures = ["foto1", "foto2"], slots=[datetime.now()], characteristics= ["Arepas", "Cafeteria"], features= ["Estacionamiento"],vacations=[datetime.now()], reservationLeadTime=10,menu="comidas.url")
    venue.open()
    update = Update(close=True)
    venue = update.modify(venue)
    assert venue.get_status() == Closed().get_status()

def test_a_new_venue_has_no_id():
    venue = create_venue("La Pizzeria", "123 Main St", 50, logo="foto.url", pictures = ["foto1", "foto2"], slots=[datetime.now()], characteristics= ["Arepas", "Cafeteria"], features= ["Estacionamiento"],vacations=[datetime.now()], reservationLeadTime=10,menu="comidas.url")
    assert not venue.id

def test_a_schema_has_an_id():
    venue = create_venue("La Pizzerias", "126 Main St", 51, logo="foto.url", pictures = ["foto1", "foto2"], slots=[datetime.now()], characteristics= ["Arepas", "Cafeteria"], features= ["Estacionamiento"],vacations=[datetime.now()], reservationLeadTime=10,menu="comidas.url")
    assert venue.persistance().id != ""

def test_after_persisting_a_venue_it_can_be_recovered_with_its_id():
    venue = create_venue("La Pizzeria", "123 Main St", 50, logo="foto.url", pictures = ["foto1", "foto2"], slots=[datetime.now()], characteristics= ["Arepas", "Cafeteria"], features= ["Estacionamiento"],vacations=[datetime.now()], reservationLeadTime=10,menu="comidas.url")
    base = MockBase()
    venue_with_id=venue.persistance()
    base.store_venue(venue_with_id)
    assert base.get_venue_by_id(venue_with_id.id) == venue_with_id

def test_after_deleting_a_venue_it_can_no_longer_be_recovered():
    venue = create_venue("La Pizzerias", "126 Main St", 51, logo="foto.url", pictures = ["foto1", "foto2"], slots=[datetime.now()], characteristics= ["Arepas", "Cafeteria"], features= ["Estacionamiento"],vacations=[datetime.now()], reservationLeadTime=10,menu="comidas.url")
    base = MockBase()
    base.store_venue(venue.persistance())
    assert base.get_venue_by_id(venue.id) != None
    #Deleting the reservation
    Venue.delete(venue.id, base)
    assert base.get_venue_by_id(venue.id) == None

def get_locations() -> List[str]:
    return ["-34.694174,-58.5566507", "-34.794174,-58.6566507", "-34.894174,-58.7566507", "-34.994174,-58.8566507", "-35.094174,-58.9566507"] 

def create_venues_by_distance() -> List[Venue]:
    locations = get_locations()
    shuffle(locations)
    venues = [create_venue("La Pizzerias", 
                           loc, 51, logo="foto.url", pictures = ["foto1", "foto2"], 
                           slots=[datetime.now()], characteristics= ["Arepas", "Cafeteria"], features= ["Estacionamiento"],
                           vacations=[datetime.now()], reservationLeadTime=10,menu="comidas.url")
            for loc in locations]
    return venues



def test_venue_ranking_by_distance():
    my_location = ("-34.594174","-58.4566507")
    base = MockBase()

    for venue in create_venues_by_distance():
        base.store_venue(venue.persistance())
    ranker = Ranker(base, my_location)
    result = [value.venue.location for value in asyncio.run(ranker.rank())]
    locations = get_locations()
    all_equal = list(filter(
        lambda x: x[0] == x[1],
        zip(result, locations)
    ))
    assert len(all_equal) == len(locations) #This means all locations are equal (and get_locations returns locations unsorted)
