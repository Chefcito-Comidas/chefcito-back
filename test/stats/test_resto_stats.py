import asyncio
import datetime
import pytest

from src.model.reservations.reservation import Assisted, Canceled, Expired, Reservation
from src.model.stats.data.base import MockedStatsDB
from src.model.stats.provider import LocalStatsProvider
from src.model.stats.stats_update import StatsUpdate


def test_on_canceled_reservation():
    db = MockedStatsDB()
    stats = LocalStatsProvider(db)

    reservation = Reservation(id="123", user="", venue="SomeVenue", time=datetime.datetime.now(tz=datetime.timezone.utc), status=Canceled(), people=4)

    asyncio.run(stats.update(reservation))

    user = asyncio.run(stats.get_venue("SomeVenue"))

    assert user.canceled == 1.0
    assert user.total == 1

def test_on_expired_reservation():
    db = MockedStatsDB()
    stats = LocalStatsProvider(db)


    reservation = Reservation(id="123", user="", venue="SomeVenue", time=datetime.datetime.now(tz=datetime.timezone.utc), status=Expired(), people=4)

    asyncio.run(stats.update(reservation))

    user = asyncio.run(stats.get_venue("SomeVenue"))

    assert user.expired == 1.0
    assert user.total == 1

def test_on_efective_reservation():
    db = MockedStatsDB()
    stats = LocalStatsProvider(db)


    reservation = Reservation(id="123", user="", venue="SomeVenue", time=datetime.datetime.now(tz=datetime.timezone.utc), status=Assisted(), people=4)

    asyncio.run(stats.update(reservation))

    user = asyncio.run(stats.get_venue("SomeVenue"))

    assert user.canceled == 0
    assert user.expired == 0
    assert user.total == 1

def test_on_multiple_reservations():
    db = MockedStatsDB()
    stats = LocalStatsProvider(db)


    reservation = Reservation(id="123", user="", venue="SomeVenue", time=datetime.datetime.now(tz=datetime.timezone.utc), status=Assisted(), people=4)

    asyncio.run(stats.update(reservation))
    reservation.status = Canceled()
    asyncio.run(stats.update(reservation))
    reservation.status = Expired()
    asyncio.run(stats.update(reservation))

    user = asyncio.run(stats.get_venue("SomeVenue"))

    assert user.canceled == 1/3
    assert user.expired == 1/3
    assert user.total == 3

def test_on_reservation_update():
    db = MockedStatsDB()
    stats = LocalStatsProvider(db)

    update = Reservation(
        id="Random",
        user="SomeUser",
        venue="SomeVenue",
        time=datetime.datetime.now(),
        people=5,
        status=Assisted()
    )

    asyncio.run(stats.update(update))

    venue = asyncio.run(stats.get_venue("SomeVenue"))

    assert venue.total == 1
    assert venue.people == 5

def test_on_many_reservations_updates():
    db = MockedStatsDB()
    stats = LocalStatsProvider(db)

    update = Reservation(
        id="Random",
        user="SomeUser",
        venue="SomeVenue",
        time=datetime.datetime.now(),
        people=4,
        status=Assisted()
    )

    asyncio.run(stats.update(update))
    update.people = 4
    asyncio.run(stats.update(update))
    update.people = 9
    asyncio.run(stats.update(update))

    venue = asyncio.run(stats.get_venue("SomeVenue"))

    assert venue.total == 3
    assert round(venue.people) == 9

def test_on_reservations_each_day():
    db = MockedStatsDB()
    stats = LocalStatsProvider(db)

    update = Reservation(
        id="Random",
        user="SomeUser",
        venue="SomeVenue",
        time=datetime.datetime(year=2024, month=4, day=14), #It was a Sunday (day 6)
        people=5,
        status=Assisted()
    )

    asyncio.run(stats.update(update))
    for i in range(6):
        update = Reservation(
        id="Random",
        user="SomeUser",
        venue="SomeVenue",
        time=datetime.datetime(year=2024, month=4, day=14) + datetime.timedelta(days=1+i),
        people=5,
        status=Assisted()
    )
        asyncio.run(stats.update(update))

    venue = asyncio.run(stats.get_venue("SomeVenue"))

    assert venue.total == 7
    for i in range(7):
        assert round(venue.get_day(i),2) == round(1/7, 2)

def test_on_reservation_turns():
    db = MockedStatsDB()
    stats = LocalStatsProvider(db)

    for i in range(9):
        update = Reservation(
        id="Random",
        user="SomeUser",
        venue="SomeVenue",
        time=datetime.datetime(year=2024, month=4, day=14, hour=20) + datetime.timedelta(hours=i%3),
        people=5,
        status=Assisted()
    )
        asyncio.run(stats.update(update))

    venue = asyncio.run(stats.get_venue("SomeVenue"))

    assert venue.total == 9
    for turn in venue.get_turns():
       assert round(turn[1], 2) == round(1/3, 2)
