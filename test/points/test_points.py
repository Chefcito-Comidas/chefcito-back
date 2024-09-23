import asyncio
import datetime
import pytest

from src.model.opinions.opinion import Opinion
from src.model.points.data.base import MockedPointBase
from src.model.points.point import Point
from src.model.reservations.reservation import Assisted, Canceled, Expired, Reservation
from src.model.reservations.update import Update


def test_a_canceled_reservation_gives_negative_points():
    reservation = Reservation(
        id="reservation",
        user="User",
        venue="Venue",
        time=datetime.datetime.now(),
        people=3,
        status=Canceled()
    )
    points = Point.from_reservation(reservation)
    assert points.total == -50

def test_a_confirmed_reservation_gives_positive_points():
    reservation = Reservation(
        id="reservation",
        user="User",
        venue="Venue",
        time=datetime.datetime.now(),
        people=3,
        status=Assisted()
    )
    points = Point.from_reservation(reservation)
    assert points.total == 50

def test_an_expired_reservation_gives_negative_points():
    reservation = Reservation(
        id="reservation",
        user="User",
        venue="Venue",
        time=datetime.datetime.now(),
        people=3,
        status=Expired()
    )
    points = Point.from_reservation(reservation)
    assert points.total == -50

def test_a_canceled_reservation_by_the_venue_does_not_generate_points():
    reservation = Reservation(
        id="reservation",
        user="User",
        venue="Venue",
        time=datetime.datetime.now(),
        people=3,
        status=Canceled()
    )
    update = Update(user="user/Venue")
    points = Point.from_reservation(reservation, updater=update.user)
    assert points.total == 0

def test_creation_for_opinion():
    reservation = Reservation(
        id="reservation",
        user="User",
        venue="Venue",
        time=datetime.datetime.now(),
        people=3,
        status=Assisted()
    )
    points = Point.from_opinion(reservation)
    assert points.total == 50

def test_storing_and_recovering_points():
    base = MockedPointBase()
    user_name = "User"

    points = Point(
        total=100,
        user=user_name
    )

    asyncio.run(base.update_points(points))
    recovered = asyncio.run(base.recover_points(user_name))
    assert recovered.total == points.total


def test_storing_and_updating_points():
    base = MockedPointBase()
    user_name = "User"

    points = Point(
        total=100,
        user=user_name
    )

    asyncio.run(base.update_points(points))
    
    points.total = 300
    asyncio.run(base.update_points(points))
    recovered = asyncio.run(base.recover_points(user_name))
    assert recovered.total == 400 


