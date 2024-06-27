import pytest
from src.model.venues.venue import Venue, create_venue, Available, Closed, Unconfirmed, Occupied
from src.model.venues.update import Update

def test_new_venue_is_open():
    venue = create_venue("La Pizzeria","125 Main St", 50)
    assert venue.get_status() == Available().get_status()

def test_closing_a_venue_changes_status_to_closed():
    venue = create_venue(name="La Pizzeria", location="123 Main St", capacity=50)
    venue.close()
    assert venue.get_status() == Closed().get_status()

def test_opening_a_closed_venue_changes_status_to_open():
    venue = create_venue(name="La Pizzeria", location="123 Main St", capacity=50)
    venue.close()
    venue.open()
    assert venue.get_status() == Available().get_status()

def test_updating_a_venue_changes_its_attributes():
    venue = create_venue(name="La Pizzeria", location="123 Main St", capacity=50)
    update = Update(name="La Trattoria", location="456 Main St", capacity=60)
    updated_venue = update.modify(venue)
    assert updated_venue.name == "La Trattoria"
    assert updated_venue.location == "456 Main St"
    assert updated_venue.capacity == 60
    assert updated_venue.get_status() == Unconfirmed().get_status()  # Asumiendo que el estado cambia a Uncomfirmed tras la modificación

def test_occupying_a_venue_changes_status_to_occupied():
    venue = create_venue(name="La Pizzeria", location="123 Main St", capacity=50)
    update = Update(occupy=True)
    updated_venue = update.modify(venue)
    assert updated_venue.get_status() == Occupied().get_status()
