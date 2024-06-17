import pytest
from src.model.reservations.reservation import Accepted, Canceled, Uncomfirmed, create_reservation
from src.model.reservations.update import Update


def test_new_reservation_is_not_confirmed():
    reservation = create_reservation("user", "venue", "at", 5)
    assert reservation.get_status() == Uncomfirmed().get_status() 


def test_an_unaccepted_reservation_is_canceled():
    reservation = create_reservation("user", "venue", "at", 6)
    reservation.reject()
    assert reservation.get_status() == Canceled().get_status()

def test_an_accepted_reservation_is_confirmed():
    reservation = create_reservation("user", "venue", "at", 10)
    reservation.accept()
    assert reservation.get_status() == Accepted().get_status()

def test_a_confirmed_reservation_is_unconfirmed_when_modified():
    reservation = create_reservation("user", "venue", "at", 2)
    update = Update(people=3)
    reservation = update.modify(reservation)
    assert reservation.get_status() == Uncomfirmed().get_status() 

 