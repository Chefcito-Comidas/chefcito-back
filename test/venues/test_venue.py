import pytest
from src.model.venues.venue import create_venue, Available, Closed, Unconfirmed, Occupied
from src.model.venues.update import Update
from src.model.venues.data.base import MockBase


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

def test_the_venue_can_close_through_an_update():
    venue = create_venue("La Pizzeria", "123 Main St", 50)
    venue.open()
    update = Update(close=True)
    venue = update.modify(venue)
    assert venue.get_status() == Closed().get_status()

def test_a_new_venue_has_no_id():
    venue = create_venue("La Pizzeria", "123 Main St", 50)
    assert not venue.id

def test_a_schema_has_an_id():
    venue = create_venue("La Pizzerias", "126 Main St", 51)
    assert venue.persistance().id != ""

def test_after_persisting_a_venue_it_can_be_recovered_with_its_id():
    venue = create_venue("La Pizzeria", "123 Main St", 50)
    base = MockBase()
    venue_with_id=venue.persistance()
    base.store_venue(venue_with_id)
    assert base.get_venue_by_id(venue_with_id.id) == venue_with_id