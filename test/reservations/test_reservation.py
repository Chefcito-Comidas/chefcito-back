from datetime import datetime
import pytest
from src.model.reservations.data.base import MockBase
from src.model.reservations.data.schema import ReservationSchema
from src.model.reservations.reservation import Accepted, Canceled, Reservation, Uncomfirmed, create_reservation
from src.model.reservations.update import Update


def test_new_reservation_is_not_confirmed():
    reservation = create_reservation("user", "venue", datetime.now(), 5)
    assert reservation.get_status() == Uncomfirmed().get_status() 


def test_an_unaccepted_reservation_is_canceled():
    reservation = create_reservation("user", "venue", datetime.now(), 6)
    reservation.reject()
    assert reservation.get_status() == Canceled().get_status()

def test_an_accepted_reservation_is_confirmed():
    reservation = create_reservation("user", "venue", datetime.now(), 10)
    reservation.accept()
    assert reservation.get_status() == Accepted().get_status()

def test_a_confirmed_reservation_is_unconfirmed_when_modified():
    reservation = create_reservation("user", "venue", datetime.now(), 2)
    update = Update(people=3, user="user")
    reservation = update.modify(reservation)
    assert reservation.get_status() == Uncomfirmed().get_status() 

def test_the_user_cannot_accept_through_an_update():
    reservation = create_reservation("user", "venue", datetime.now(), 3)
    update = Update(accept=True, user="user")
    reservation = update.modify(reservation)
    assert reservation.get_status() == Uncomfirmed().get_status()

def test_the_venue_can_accept_through_an_update():
    reservation = create_reservation("user", "venue", datetime.now(), 2)
    update = Update(accept=True, user="venue")
    reservation = update.modify(reservation)
    assert reservation.get_status() == Accepted().get_status()

def test_a_new_reservation_has_no_id():
    reservation = create_reservation("user", "venue", datetime.now(), 3)
    assert not reservation.id

def test_a_schema_has_an_id():
    reservation = create_reservation("user", "venue", datetime.now(), 6)
    assert reservation.persistance().id != "" 

def test_after_persisting_a_reservation_it_can_be_recovered_with_its_id():
    reservation = create_reservation("user", "venue", datetime.now(), 9)
    base = MockBase()
    reservation_with_id=reservation.persistance()
    base.store_reservation(reservation_with_id)
    assert base.get_reservation_by_id(reservation.id) == reservation_with_id

def test_after_deleting_a_reservation_it_can_no_longer_be_recovered():
    reservation = create_reservation("user", "venue", datetime.now(), 2)
    base = MockBase()
    base.store_reservation(reservation.persistance())

    #Deleting the reservation
    Reservation.delete(reservation.id, base)
    assert base.get_reservation_by_id(reservation.id) == None
