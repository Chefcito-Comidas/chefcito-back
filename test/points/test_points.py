import asyncio
import datetime
import pytest

from src.model.points.data.base import MockedPointBase
from src.model.points.point import Point, PointResponse
from src.model.points.provider import LocalPointsProvider
from src.model.reservations.reservation import Assisted, Canceled, Expired, Reservation
from src.model.reservations.update import Update


def test_a_canceled_reservation_gives_negative_points():
    reservation = Reservation(
        id="reservation",
        user="User",
        venue="Venue",
        time=datetime.datetime.now(),
        people=3,
        status=Canceled()
    )
    points = Point.from_reservation(reservation)
    assert points.total == -50

def test_a_confirmed_reservation_gives_positive_points():
    reservation = Reservation(
        id="reservation",
        user="User",
        venue="Venue",
        time=datetime.datetime.now(),
        people=3,
        status=Assisted()
    )
    points = Point.from_reservation(reservation)
    assert points.total == 50

def test_an_expired_reservation_gives_negative_points():
    reservation = Reservation(
        id="reservation",
        user="User",
        venue="Venue",
        time=datetime.datetime.now(),
        people=3,
        status=Expired()
    )
    points = Point.from_reservation(reservation)
    assert points.total == -50

def test_a_canceled_reservation_by_the_venue_does_not_generate_points():
    reservation = Reservation(
        id="reservation",
        user="User",
        venue="Venue",
        time=datetime.datetime.now(),
        people=3,
        status=Canceled()
    )
    update = Update(user="user/Venue")
    points = Point.from_reservation(reservation, updater=update.user)
    assert points.total == 0

def test_creation_for_opinion():
    reservation = Reservation(
        id="reservation",
        user="User",
        venue="Venue",
        time=datetime.datetime.now(),
        people=3,
        status=Assisted()
    )
    points = Point.from_opinion(reservation)
    assert points.total == 50

def test_storing_and_recovering_points():
    base = MockedPointBase()
    user_name = "User"

    points = Point(
        total=100,
        user=user_name
    )

    asyncio.run(base.update_points(points))
    recovered = asyncio.run(base.recover_points(user_name))
    assert recovered.total == points.total #type: ignore


def test_storing_and_updating_points():
    base = MockedPointBase()
    user_name = "User"

    points = Point(
        total=100,
        user=user_name
    )

    asyncio.run(base.update_points(points))
    
    points.total = 300
    asyncio.run(base.update_points(points))
    recovered = asyncio.run(base.recover_points(user_name))
    assert recovered.total == 400 #type: ignore 

def test_a_user_with_no_points_level():
    base = MockedPointBase()
    user_name = "User"
    asyncio.run(base.update_points(Point(user=user_name, total=0)))

    recovered = asyncio.run(base.recover_points(user_name))
    assert recovered is not None
    assert recovered.get_level() == 0

def test_a_user_with_100_points_is_level_1():
    base = MockedPointBase()
    user_name = "User"

    points = Point(
            total=100,
            user=user_name
            )
    
    asyncio.run(base.update_points(points))
    recovered = asyncio.run(base.recover_points(user_name))
    assert recovered is not None
    assert recovered.get_level() == 1
    

def test_a_user_with_x_points_is_level_n():
    base = MockedPointBase()
    user_name_base = "User_"

    i = 0

    while i < 10:
        points = Point(
                total=100 * ((2**i)-1),
                user=user_name_base + str(i)
                )

        asyncio.run(base.update_points(points))
        recovered = asyncio.run(base.recover_points(user_name_base+str(i)))
        assert recovered is not None
        assert recovered.get_level() == i
        i += 1
       
def test_point_into_response():
    point = Point(user="User", total=100)
    expected = PointResponse(user="User", total=100, level="first stepper")
    assert expected == point.into_response(levels=["baby", "first stepper", "great man"])

def test_point_into_various_levels():
    levels = ["baby", "first stepper", "little kid", "teenager", "adult", "old man"]
    i = 0
    while i < 10:
        point = Point(user="User", total=100*((2**i)-1))
        expected = PointResponse(user="User", total=100*((2**i)-1), level=levels[i] if i < 5 else levels[-1])
        assert point.into_response(levels=levels) == expected
        i += 1

def test_local_service_response():
    base = MockedPointBase()
    levels = ["baby", "first stepper", "little kid", "teenager", "adult", "old man"]
    provider = LocalPointsProvider(base, levels=levels)
    user_name_base = "User_"
    i = 0
    while i < 10:
        points = Point(
                total=100 * ((2**i)-1),
                user=user_name_base + str(i)
                )
        expected = PointResponse(user=user_name_base+str(i), total=100*((2**i)-1), level=levels[i] if i < 5 else levels[-1])
        asyncio.run(provider.update_points(points))
        recovered = asyncio.run(provider.get_points(user_name_base+str(i)))
        assert recovered is not None
        assert recovered == expected
        i += 1
       

