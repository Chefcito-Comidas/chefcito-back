import asyncio
from datetime import datetime, timedelta
from typing import List
import pytest
from testcontainers.mongodb import MongoDbContainer

from src.model.opinions.data.base import MongoOpinionsDB, OpinionsDB
from src.model.opinions.opinion import Opinion
from src.model.opinions.opinion_query import OpinionQuery
from src.model.opinions.provider import LocalOpinionsProvider
from src.model.opinions.service import OpinionsService
from src.model.summarizer.process.algorithm import SummaryAlgorithm
from src.model.summarizer.provider import SummarizerService
from src.model.summarizer.service import LocalSummarizerProvider
from src.model.summarizer.summary import Summary

async def opinion_load_and_queried_by_venue(database: OpinionsDB):
    provider = LocalOpinionsProvider(database, None) # type: ignore
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
        assert result.result.pop() == opinion
    except Exception as e:
        pytest.fail(
                reason=f"Failed at opinion_load_and_queried_by_venue because of {e}"
                )

def create_many_by_daterange(from_date: datetime, to_date: datetime) -> List[Opinion]:
    dates = []
    while from_date < to_date:
        dates.append(from_date)
        from_date = from_date + timedelta(hours=1)
    
    result = []

    for index, date in enumerate(dates):
        result.append(Opinion(
            venue=f"Venue_{index}",
            reservation=f"Reservation_{index}",
            date=date,
            opinion="Normal opinion"
            ))

    return result


async def opinions_load_and_queried_by_date(database: OpinionsDB):
    provider = LocalOpinionsProvider(database, None) # type: ignore
    dates_range = create_many_by_daterange(datetime(2024, 7, 25, 20, 0, 0), 
                                           datetime(2024, 7, 26, 20, 0, 0))
    for value in list(                    
        map(
            lambda opinion:  provider.create_opinion(opinion),
            dates_range
        )
                      ):
        await value
    
    

    first_query = OpinionQuery(
            from_date=datetime(2024, 7, 25, 20, 0, 0),
            to_date=datetime(2024, 7, 26, 8, 0, 0),
            limit=20
            )
    second_query = OpinionQuery(
            from_date=datetime(2024, 7, 26, 9, 0, 0),
            to_date=datetime(2024, 7, 26, 20, 0, 0),
            limit=20
            )

    first_result = await provider.query_opinions(first_query)
    second_result = await provider.query_opinions(second_query)

    try:
        assert first_result.total == 13, f"First result length: {first_result.total}" 
        assert second_result.total == 11, f"Second result length: {second_result.total}"
        assert all(map(lambda op: datetime(2024, 7, 25, 20, 0, 0) <= op.date <= datetime(2024, 7, 26, 8, 0, 0),first_result.result)), f"first result mappings"
        assert all(map(lambda op: datetime(2024, 7, 26, 9, 0, 0) <= op.date <= datetime(2024, 7, 26, 20, 0, 0),second_result.result)), f"second result mappings"
        assert sorted(first_result.result, key=lambda x: x.date, reverse=True) == first_result.result, f"sorted answer"
    except Exception as e:
        pytest.fail(reason=f"failed at opinions_load_and_queried_by_date: {e}")

    
async def storing_and_retrieving_summaries(database: OpinionsDB):
    service = LocalOpinionsProvider(database, LocalSummarizerProvider(database, SummaryAlgorithm()))
    await service.create_opinion(Opinion(
        venue="TestSummaryVenue",
        opinion="This is an opinion",
        reservation="123",
        date=datetime.now()
    ))
    generated = await service.create_venue_summary("TestSummaryVenue")
    if not isinstance(generated, Summary):
        pytest.fail(reason=f"Error generating Summary: {generated}")
    summary = await service.get_venue_summary("TestSummaryVenue")
    assert summary.text == "This is an opinion"


@pytest.mark.asyncio
async def test_opinions_loop():
    with MongoDbContainer() as mongo:
        conn_string = mongo.get_connection_url()
        database = MongoOpinionsDB(conn_string)
        await database.init()
        await opinion_load_and_queried_by_venue(database) 
        await opinions_load_and_queried_by_date(database)
        await storing_and_retrieving_summaries(database)
