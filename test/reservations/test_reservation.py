import asyncio
from datetime import datetime,timezone
import pytest
from src.model.opinions.data.base import MockedOpinionsDB
from src.model.opinions.provider import LocalOpinionsProvider
from src.model.reservations.data.base import MockBase
from src.model.reservations.reservation import CreateInfo
from src.model.reservations.data.schema import ReservationSchema
from src.model.reservations.reservation import Accepted, Canceled, Reservation, Uncomfirmed, create_reservation
from src.model.reservations.service import LocalReservationsProvider
from src.model.reservations.update import Update
from src.model.reservations.reservationQuery import ReservationQuery
from src.model.stats.data.base import MockedStatsDB
from src.model.stats.provider import LocalStatsProvider
from src.model.users.permissions.base import DBMock
from src.model.users.service import LocalUsersProvider, UsersProvider
from src.model.venues.service import LocalVenuesProvider
import src.model.venues.data.base as v_base
import src.model.venues.venue as v
from src.model.venues.venueQuery import VenueQuery


def get_mocked_users() -> UsersProvider:
    return LocalUsersProvider(None, DBMock({}, {}), None)

def test_new_reservation_is_not_confirmed():
    reservation = create_reservation("user", "venue", datetime.now(), 5)
    assert reservation.get_status() == Uncomfirmed().get_status()


def test_an_unaccepted_reservation_is_canceled():
    reservation = create_reservation("user", "venue", datetime.now(), 6)
    reservation.advance(forward=False, who="user/venue")
    assert reservation.get_status() == Canceled().get_status()

def test_an_accepted_reservation_is_confirmed():
    reservation = create_reservation("user", "venue", datetime.now(), 10)
    reservation.advance(forward=True, who="user/venue")
    assert reservation.get_status() == Accepted().get_status()

def test_a_confirmed_reservation_is_unconfirmed_when_modified():
    reservation = create_reservation("user", "venue", datetime.now(), 2)
    update = Update(people=3, user="user")
    provider = LocalStatsProvider(MockedStatsDB())
    reservation = asyncio.run(update.modify(reservation, provider, None))
    assert reservation.get_status() == Uncomfirmed().get_status()

def test_the_user_cannot_accept_through_an_update():
    reservation = create_reservation("user", "venue", datetime.now(), 3)
    update = Update(advance_forward=True, user="user")
    provider = LocalStatsProvider(MockedStatsDB())
    reservation = asyncio.run(update.modify(reservation, provider, None))
    assert reservation.get_status() == Uncomfirmed().get_status()

def test_the_venue_can_accept_through_an_update():
    reservation = create_reservation("user", "venue", datetime.now(), 2)
    update = Update(advance_forward=True, user="user/venue")
    provider = LocalStatsProvider(MockedStatsDB())
    reservation = asyncio.run(update.modify(reservation,provider, None))
    assert reservation.get_status() == Accepted().get_status()

def test_a_new_reservation_has_no_id():
    reservation = create_reservation("user", "venue", datetime.now(), 3)
    assert not reservation.id

def test_a_schema_has_an_id():
    reservation = create_reservation("user", "venue", datetime.now(), 6)
    assert reservation.persistance().id != ""

def test_after_persisting_a_reservation_it_can_be_recovered_with_its_id():
    reservation = create_reservation("user", "venue", datetime.now(), 9)
    base = MockBase()

    base.store_reservation(reservation.persistance())
    result = base.get_reservation_by_id(reservation.id)
    assert result != None
    assert result.id == reservation.id


def test_after_deleting_a_reservation_it_can_no_longer_be_recovered():
    reservation = create_reservation("user", "venue", datetime.now(), 2)
    base = MockBase()
    base.store_reservation(reservation.persistance())

    #Deleting the reservation
    Reservation.delete(reservation.id, base)
    assert base.get_reservation_by_id(reservation.id) == None

def test_a_reservation_cannot_be_done_if_the_venue_does_not_exists():
    database = MockBase()
    venues_db = v_base.MockBase()
    venues = LocalVenuesProvider(venues_db)
    provider = LocalStatsProvider(MockedStatsDB())
    service = LocalReservationsProvider(database, venues, None, provider, None, get_mocked_users()) # type: ignore

    reservation = CreateInfo(user="juanCarlos",
                             venue="Lo de Carlitos",
                             time=datetime.now(),
                             people=9)

    pytest.raises(Exception, lambda: asyncio.run(service.create_reservation(reservation)))

def test_a_reservation_is_done_if_the_venue_does_exist():
    database = MockBase()
    venues_db = v_base.MockBase()
    venues = LocalVenuesProvider(venues_db)
    opinions = LocalOpinionsProvider(MockedOpinionsDB(), None)
    provider = LocalStatsProvider(MockedStatsDB())
    service = LocalReservationsProvider(database, venues, opinions, provider, None, get_mocked_users())
    asyncio.run(venues.create_venue(v.CreateInfo(
                                                 id="ADSAF",
                                                 name="Lo de Carlitos",
                                                 logo="SomeCoolLogo",
                                                 pictures=[],
                                                 slots=[],
                                                 location="almendra 270",
                                                 capacity=150,
                                                 characteristics= ["Arepas", "Cafeteria"],
                                                 features= ["Estacionamiento"],
                                                 vacations=[datetime.now()],
                                                 reservationLeadTime=10,
                                                 menu="Menu")))

    id = asyncio.run(venues.get_venues(VenueQuery())).result.pop().id

    reservation = CreateInfo(user="juanCarlos",
                             venue=id,
                             time=datetime.now().replace(tzinfo=timezone.utc),
                             people=9)

    asyncio.run(service.create_reservation(reservation))
    reservation_venue_id = asyncio.run(service.get_reservations(ReservationQuery())).result.pop().venue

    assert reservation_venue_id == id
