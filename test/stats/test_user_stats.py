import asyncio
import pytest

from src.model.stats.data.base import MockedStatsDB
from src.model.stats.provider import LocalStatsProvider
from src.model.stats.stats_query import StatsQuery
from src.model.stats.stats_update import StatsUpdate


def test_on_cancel_update():
    db = MockedStatsDB()
    stats = LocalStatsProvider(db)

    update = StatsUpdate(user="SomeClient")
    update.canceled_reservation()

    asyncio.run(stats.update(update))

    user = asyncio.run(stats.get_user("SomeClient"))

    assert user.canceled == 1.0    