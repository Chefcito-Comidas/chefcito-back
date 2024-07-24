from datetime import datetime
import pytest
from testcontainers.mongodb import MongoDbContainer

from src.model.opinions.data.base import MongoOpinionsDB, OpinionsDB
from src.model.opinions.opinion import Opinion
from src.model.opinions.opinion_query import OpinionQuery
from src.model.opinions.service import LocalOpinionsProvider

async def opinion_load_and_queried_by_venue(database: OpinionsDB):
    provider = LocalOpinionsProvider(database)
    opinion = Opinion(
            venue="Elegantland",
            reservation="aReservationID",
            date=datetime(2024, 7, 24, 20, 20, 45),
            opinion="Sehr ruhig und bequem aber auch sehr teur"
            )
    try:
        await provider.create_opinion(opinion)
        query = OpinionQuery(venue="Elegantland")
        result = await provider.query_opinions(query)
        print(f"{result} vs. {opinion}")
        assert result.pop() == opinion
    except Exception as e:
        pytest.fail(
                reason=f"Failed at opinion_load_and_queried_by_venue because of {e}"
                )


@pytest.mark.asyncio
async def test_opinions_loop():
    with MongoDbContainer() as mongo:
        conn_string = mongo.get_connection_url()
        database = MongoOpinionsDB(conn_string)
        await database.init()
        await opinion_load_and_queried_by_venue(database) 


