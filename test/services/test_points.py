import pytest
from sqlalchemy import create_engine
from testcontainers.postgres import PostgresContainer
from src.model.points.data.base import RelPointBase
from src.model.points.data.schema import PointsBaseSchema, PointSchema
from src.model.points.point import Point
from src.model.points.provider import LocalPointsProvider
from src.model.points.service import PointService

def config(url: str):
    engine = create_engine(url)
    PointsBaseSchema.metadata.create_all(engine)

async def store_user_points(base: RelPointBase):
    points = Point(total=100, user="User_1")
    await base.update_points(points)
    recovered = await base.recover_points("User_1")
    assert not recovered is None
    assert recovered.total == points.total

async def update_user_points(base: RelPointBase):
    """
        Builds over store_user_points
    """
    points = Point(total=100, user="User_1")
    await base.update_points(points)
    recovered = await base.recover_points("User_1")
    assert not recovered is None
    assert recovered.total == 100 * 2

async def service_query_making(base: RelPointBase):
    provider = LocalPointsProvider(base)
    service = PointService(provider) 
    points = Point(total=100, user="User_2")
    await service.store_points(points)
    points_1 = await service.get_points("User_1")
    assert points_1.total == 200
    points_2 = await service.get_points("User_2")
    assert points_2.total == 100

async def service_levels_test(base: RelPointBase):
    levels = ["baby", "kid", "teen", "adult", "old"]
    provider = LocalPointsProvider(base, levels=levels)
    service = PointService(provider)
    user_base = "User_level_"
    for i in range(0, 11):
        await service.store_points(Point(
            user=user_base+str(i),
            total=100*((2**i)-1)
            ))
        result = await service.get_points(user_base+str(i))
        assert result.level == levels[i] if i < 5 else levels[4]



async def service_update_making(base: RelPointBase):
    """
        Builds over service_query_making
    """
    provider = LocalPointsProvider(base)
    service = PointService(provider)
    points = Point(total=100, user="User_2")
    await service.store_points(points)
    points = await service.get_points("User_2")
    assert points.total == 200

@pytest.mark.asyncio
async def test_points_loop():
    with PostgresContainer('postgres:16') as postgres:
        config(postgres.get_connection_url())
        db = RelPointBase(postgres.get_connection_url())
        await store_user_points(db)
        await update_user_points(db)
        await service_query_making(db)
        await service_update_making(db)
        await service_levels_test(db)
