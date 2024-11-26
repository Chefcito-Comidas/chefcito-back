import asyncio
import datetime
import pytest

from src.model.reservations.reservation import Assisted, Canceled, Expired, Reservation
from src.model.stats.data.base import MockedStatsDB
from src.model.stats.provider import LocalStatsProvider
from src.model.stats.stats_update import StatsUpdate


def test_on_cancel_update():
    db = MockedStatsDB()
    stats = LocalStatsProvider(db)


    update = Reservation(
        id="Random",
        user="SomeClient",
        venue="SomeVenue",
        time=datetime.datetime(year=2024, month=4, day=14, hour=20),
        people=5,
        status=Canceled()
    )
    asyncio.run(stats.update(update))

    user = asyncio.run(stats.get_user("SomeClient"))

    assert user.canceled == 1.0
    assert user.total == 1

def test_on_expired_update():
    db = MockedStatsDB()
    stats = LocalStatsProvider(db)


    update = Reservation(
        id="Random",
        user="SomeClient",
        venue="SomeVenue",
        time=datetime.datetime(year=2024, month=4, day=14, hour=20),
        people=5,
        status=Expired()
    )
    asyncio.run(stats.update(update))

    user = asyncio.run(stats.get_user("SomeClient"))

    assert user.expired == 1.0
    assert user.total == 1

def test_on_cancel_and_expired():
    db = MockedStatsDB()
    stats = LocalStatsProvider(db)
    update = Reservation(
        id="Random",
        user="SomeClient",
        venue="SomeVenue",
        time=datetime.datetime(year=2024, month=4, day=14, hour=20),
        people=5,
        status=Canceled()
    )

    asyncio.run(stats.update(update))
    update.status = Expired()
    asyncio.run(stats.update(update))

    user = asyncio.run(stats.get_user("SomeClient"))

    assert user.expired == user.canceled == 0.5
    assert user.total == 2

def test_on_too_many_expired():
    db = MockedStatsDB()
    stats = LocalStatsProvider(db)

    for i in range(10):
        update = Reservation(
                id="SomeID",
                user="SomeUser",
                venue="RandomVenue",
                time=datetime.datetime.now(),
                people=5,
                status=Assisted() if i%2 == 0 else Expired()
            )
        asyncio.run(stats.update(update))

    threshold = 0.4
    assert asyncio.run(stats.get_user("SomeUser", expired_threshold=threshold)).expired_alert
    assert not asyncio.run(stats.get_user("SomeUser", expired_threshold=0.51)).expired_alert

def test_on_too_many_canceled():
    db = MockedStatsDB()
    stats = LocalStatsProvider(db)

    for i in range(10):
        update = Reservation(
                id="SomeID",
                user="SomeUser",
                venue="RandomVenue",
                time=datetime.datetime.now(),
                people=5,
                status=Canceled() if i%2 == 0 else Expired()
            )

        asyncio.run(stats.update(update))

    threshold = 0.4
    assert asyncio.run(stats.get_user("SomeUser", canceled_threshold=threshold)).canceled_alert
    assert not asyncio.run(stats.get_user("SomeUser", 0.51)).canceled_alert

def test_user_stats_return_valid_alerts():
    db = MockedStatsDB()
    stats = LocalStatsProvider(db)

    for i in range(101):
        update = Reservation(
                id="SomeID",
                user="SomeUser",
                venue="RandomVenue",
                time=datetime.datetime.now(),
                people=2,
                status=Expired() if i%2 == 0 else Assisted()
            )

        asyncio.run(stats.update(update))
    #Too get 51 out of 101 expired
    asyncio.run(stats.update(update)) #type: ignore

    user = asyncio.run(stats.get_user("SomeUser"))
    assert user.expired_alert
    assert not user.canceled_alert
