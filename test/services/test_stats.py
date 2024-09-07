import datetime
import pytest
from testcontainers.mongodb import MongoDbContainer

from src.model.reservations.reservation import Assisted, Reservation
from src.model.stats.data.base import MongoStatsDB, StatsDB
from src.model.stats.provider import LocalStatsProvider
from src.model.stats.stats_update import StatsUpdate
from src.model.stats.user_data import UserStatData

async def user_data_storage_and_update(db: StatsDB):
    provider = LocalStatsProvider(db)
    update = StatsUpdate(user="CustomUser", venue="CustomVenue")
    user_data = UserStatData(user="", total=0, canceled=0, expired=0) 
    for i in range(100):
        if i%3 == 0:
            update.canceled_reservation() 
            user_data.increase_canceled()
        elif i%3 == 1:
            update.expired_reservation()
            user_data.increase_expired()
        else:
            update.assisted_reservation()
            user_data.increase()

        await provider.update(update)
    user = await provider.get_user("CustomUser")
    assert user.total == 100
    assert round(user.canceled, 2) == round(user_data.canceled, 2) 
    assert round(user.expired, 2) ==  round(user_data.expired, 2)

async def venue_data_based_on_customVenue(db: StatsDB):
    provider = LocalStatsProvider(db)

    venue = await provider.get_venue("CustomVenue")

    assert venue.total == 100
    assert round(venue.total, 2) == round(33 / 100, 2)
    assert round(venue.expired, 2) == round(33/ 100, 2)
    

async def venue_data_based_on_reservations(db: StatsDB):
    provider = LocalStatsProvider(db)

    for i in range(280):
        update = StatsUpdate.from_reservation(
            Reservation(
                id="Random",
                user=f"user_{i}",
                venue="CoolPlace",
                time=datetime.datetime(year=2024, month=4, day=14, hour=20) + datetime.timedelta(days=i, hours=(i)%4),
                people=i + 1,
                status=Assisted() 
            )
        )
        await provider.update(update)

    venue = await provider.get_venue("CoolPlace")

    assert venue.total == 280 
    for i in range(6):
        assert round(venue.get_day(i), 2) == round(1/7, 2)
    for turn in venue.get_turns():
        assert round(turn[1], 2) == round(1/4, 2)


@pytest.mark.asyncio
async def test_stats_loop():
    with MongoDbContainer()as mongo:
        database = MongoStatsDB(mongo.get_connection_url())
        await database.init()
        await user_data_storage_and_update(database)
        await venue_data_based_on_reservations(database) 