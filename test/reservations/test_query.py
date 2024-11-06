

import asyncio
from datetime import datetime
from typing import List
from src.model.opinions.data.base import MockedOpinionsDB
from src.model.opinions.provider import LocalOpinionsProvider
from src.model.reservations.data.base import MockBase
from src.model.reservations.data.schema import ReservationSchema
from src.model.reservations.reservation import Reservation, Uncomfirmed, create_reservation
from src.model.reservations.reservationQuery import ReservationQuery, ReservationResponse
from src.model.users.permissions.base import DBMock
from src.model.users.service import LocalUsersProvider, UsersProvider


def get_mocked_users() -> UsersProvider:
    return LocalUsersProvider(None, DBMock({}, {}), None)

def create_reservations(amount: int) -> List[ReservationSchema]:
    """
        Creates a list of reservations for 3 users and
        2 venues with incremental ids
    """
    reservations = []
    for i in range(amount):
        reservations.append(ReservationSchema(
            id=f"{i}",
            user=f"user_{i%3}",
            venue=f"venue_{i%2}",
            time=datetime(year=2024, month=i%12 + 1, day=i%28 + 1) ,
            people=f"{i%5}",
            status=Uncomfirmed().get_status()
            )
                            )
    return reservations

def all_different(list_1: List[Reservation], list_2: List[Reservation]) -> bool:
    return not any(
            map(
                lambda x: x in list_2,
                list_1
            )
        )

def all_same_user(user: str, result: List[ReservationResponse]) -> bool:
    for reservation in result:
        if reservation.user.id != user:
            return False
    return True

def all_same_venue(venue: str, result: List[ReservationResponse]) -> bool:
    for reservation in result:
        if reservation.venue != venue:
            return False
    return True

def test_get_all_by_one_user():
    database = MockBase()
    opinions = LocalOpinionsProvider(MockedOpinionsDB(), None )
    for reservation in create_reservations(9):
        database.store_reservation(reservation)
    query = ReservationQuery(
            user="user_0"
            )
    result = asyncio.run(query.query(database, opinions, get_mocked_users()))
    assert result.total == 3

    assert all_same_user("user_0", result.result)


def test_get_all_by_one_venue():
    database = MockBase()
    opinions = LocalOpinionsProvider(MockedOpinionsDB(), None)
    for reservation in create_reservations(9):
        database.store_reservation(reservation)
    query = ReservationQuery(
            venue="venue_1"
            )
    result = asyncio.run(query.query(database, opinions, get_mocked_users()))
    assert result.total == 4
    assert all_same_venue("venue_1", result.result)

def test_limiting_the_amount_of_reservations():
    database = MockBase()
    opinions = LocalOpinionsProvider(MockedOpinionsDB(), None)
    for reservation in create_reservations(9):
        database.store_reservation(reservation)
    query = ReservationQuery(
            venue="venue_1",
            limit=2
            )
    result = asyncio.run(query.query(database, opinions, get_mocked_users()))
    assert result.total == 2
    assert all_same_venue("venue_1", result.result)

def test_stepping_with_limit_the_amount_of_reservations():
    database = MockBase()
    opinions = LocalOpinionsProvider(MockedOpinionsDB(), None)
    for reservation in create_reservations(9):
        database.store_reservation(reservation)
    query = ReservationQuery(
            venue="venue_1",
            limit=2
            )
    result_1 = asyncio.run(query.query(database, opinions, get_mocked_users()))
    query.start = 2
    result_2 = asyncio.run(query.query(database, opinions, get_mocked_users()))
    assert result_1.total == 2
    assert result_2.total == 2
    assert all_different(result_1.result, result_2.result)
