import pytest
from testcontainers.mongodb import MongoDbContainer

from src.model.stats.data.base import MongoStatsDB, StatsDB
from src.model.stats.provider import LocalStatsProvider
from src.model.stats.stats_update import StatsUpdate
from src.model.stats.user_data import UserStatData

async def user_data_storage_and_update(db: StatsDB):
    provider = LocalStatsProvider(db)
    update = StatsUpdate(user="CustomUser")
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

@pytest.mark.asyncio
async def test_stats_loop():
    with MongoDbContainer()as mongo:
        database = MongoStatsDB(mongo.get_connection_url())
        await database.init()
        await user_data_storage_and_update(database) 