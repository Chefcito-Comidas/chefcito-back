import asyncio
import pytest

from src.model.stats.data.base import MockedStatsDB
from src.model.stats.provider import LocalStatsProvider
from src.model.stats.stats_update import StatsUpdate


def test_on_canceled_reservation():
    db = MockedStatsDB()
    stats = LocalStatsProvider(db)

    update = StatsUpdate(venue="SomeVenue", user="")
    update.canceled_reservation()

    asyncio.run(stats.update(update))

    user = asyncio.run(stats.get_venue("SomeVenue"))

    assert user.canceled == 1.0
    assert user.total == 1 

def test_on_expired_reservation():
    db = MockedStatsDB()
    stats = LocalStatsProvider(db)

    update = StatsUpdate(venue="SomeVenue", user="")
    update.expired_reservation()

    asyncio.run(stats.update(update))

    user = asyncio.run(stats.get_venue("SomeVenue"))

    assert user.expired == 1.0
    assert user.total == 1 

def test_on_efective_reservation():
    db = MockedStatsDB()
    stats = LocalStatsProvider(db)

    update = StatsUpdate(venue="SomeVenue", user="")
    update.assisted_reservation()

    asyncio.run(stats.update(update))

    user = asyncio.run(stats.get_venue("SomeVenue"))

    assert user.canceled == 0
    assert user.expired == 0
    assert user.total == 1

def test_on_multiple_reservations():
    db = MockedStatsDB()
    stats = LocalStatsProvider(db)

    update = StatsUpdate(venue="SomeVenue", user="")
    update.assisted_reservation()

    asyncio.run(stats.update(update))
    update.canceled_reservation()

    asyncio.run(stats.update(update))

    update.expired_reservation()
    asyncio.run(stats.update(update))

    user = asyncio.run(stats.get_venue("SomeVenue"))

    assert user.canceled == 1/3
    assert user.expired == 1/3
    assert user.total == 3

    
