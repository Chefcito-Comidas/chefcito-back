import asyncio
from datetime import datetime
import pytest

from src.model.opinions.data.base import MockedOpinionsDB
from src.model.opinions.opinion import Opinion
from src.model.opinions.opinion_query import OpinionQuery
from src.model.opinions.provider import LocalOpinionsProvider



def test_a_created_opinion_can_be_retrieved():
    database = MockedOpinionsDB()
    provider = LocalOpinionsProvider(database, None) # type: ignore

    opinion = Opinion(
            venue="Elegantland",
            reservation="aReservationID",
            date=datetime.now(),
            opinion="Very elegant and expensive, perfect to throw away your money"
            )

    asyncio.run(provider.create_opinion(opinion))

    query = OpinionQuery(
            venue="Elegantland"
            )

    recovered_opinion = asyncio.run(provider.query_opinions(query)).result.pop()

    assert recovered_opinion == opinion

def test_opinions_from_different_restaurants_do_not_show_up_on_the_same_query():
    database = MockedOpinionsDB()
    provider = LocalOpinionsProvider(database, None) # type: ignore

    opinion = Opinion(
            venue="Elegantland",
            reservation="aReservationID",
            date=datetime.now(),
            opinion="Very elegant and expensive. I didn't like it"
            )

    opinion_2 = Opinion(
            venue="FastFoodGod",
            reservation="anotherReservationID",
            date=datetime.now(),
            opinion="Great food to gain some kilos"
            )

    list(map(lambda x: asyncio.run(provider.create_opinion(x)), [opinion, opinion_2]))
    
    query = OpinionQuery(
            venue="FastFoodGod"
            )

    result = asyncio.run(provider.query_opinions(query))

    assert result.total == 1
    assert opinion_2 in result.result
    assert opinion not in result.result

