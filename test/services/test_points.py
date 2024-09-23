import pytest
from sqlalchemy import create_engine
from testcontainers.postgres import PostgresContainer
from src.model.points.data.base import RelPointBase
from src.model.points.data.schema import PointsBaseSchema, PointSchema
from src.model.points.point import Point

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

@pytest.mark.asyncio
async def test_points_loop():
    with PostgresContainer('postgres:16') as postgres:
        config(postgres.get_connection_url())
        db = RelPointBase(postgres.get_connection_url())
        await store_user_points(db)
        await update_user_points(db)