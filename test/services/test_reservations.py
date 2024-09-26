from datetime import datetime
import pytest
from testcontainers.postgres import PostgresContainer
from src.model.opinions.data.base import MockedOpinionsDB
from src.model.opinions.provider import LocalOpinionsProvider
from src.model.points.data.base import MockedPointBase
from src.model.points.provider import LocalPointsProvider
from src.model.reservations.data.base import RelBase
from src.model.reservations.reservation import Accepted, Assisted, Reservation, Uncomfirmed, create_reservation
from src.model.reservations.reservationQuery import ReservationQuery
from src.model.reservations.update import Update
from src.model.stats.data.base import MockedStatsDB
from src.model.stats.provider import LocalStatsProvider
from test.reservations.test_query import all_different, create_reservations
from test.services.db_load import run


@pytest.mark.asyncio
async def test_reservation_persistance():
    with PostgresContainer('postgres:16') as postgres:
        run('db_config.yaml', connection=postgres.get_connection_url()) 
        reservation = create_reservation(user="user",venue="venus",time=datetime.now(),people=3)
        database = RelBase(conn_string=postgres.get_connection_url())
        database.store_reservation(reservation.persistance())
        result = database.get_reservation_by_id(reservation.id)
        assert result != None
        assert result.id == reservation.id

@pytest.mark.asyncio
async def test_reservation_update():
    with PostgresContainer('postgres:16') as postgres:
        run('db_config.yaml', connection=postgres.get_connection_url()) 
        reservation = create_reservation(user="user", venue="venue",time=datetime.now(),people=4)
        database = RelBase(conn_string=postgres.get_connection_url())
        database.store_reservation(reservation.persistance())
        update = Update(user="user/venue", advance_forward=True)
        stats = LocalStatsProvider(MockedStatsDB())
        points = LocalPointsProvider(MockedPointBase())
        reservation = await update.modify(reservation, stats, points)
        database.update_reservation(reservation.persistance())
        result = database.get_reservation_by_id(reservation.id)
        assert result != None
        assert result.status == Accepted().get_status()

@pytest.mark.asyncio
async def test_reservation_deletion():
    with PostgresContainer('postgres:16') as postgres:
        run('db_config.yaml', connection=postgres.get_connection_url()) 
        reservation = create_reservation(user="user", venue="venue",time=datetime.now(),people=4)
        database = RelBase(conn_string=postgres.get_connection_url())
        database.store_reservation(reservation.persistance())
        
        Reservation.delete(reservation.id, database)
        assert database.get_reservation_by_id(reservation.id) == None

@pytest.mark.asyncio
async def test_reservation_pagination():
    with PostgresContainer('postgres:16') as postgres:
        run('db_config.yaml', connection=postgres.get_connection_url()) 
        reservations = create_reservations(99)
        opinions = LocalOpinionsProvider(MockedOpinionsDB(), None) #type: ignore
        database = RelBase(conn_string=postgres.get_connection_url())
        for reservation in reservations:
            database.store_reservation(reservation)
        
        query = ReservationQuery(
                user="user_1",
                limit=5
                )
        result_1 = await query.query(database, opinions)
        query.start=6
        result_2 = await query.query(database, opinions)
        query.start=11
        result_3= await query.query(database, opinions)
        assert result_1.total == result_2.total == result_3.total == 33
        assert len(result_1.result) == len(result_2.result) == len(result_3.result) == 5
        assert all_different(result_1.result, result_2.result)
        assert all_different(result_1.result, result_3.result)
        assert all_different(result_2.result, result_3.result)

@pytest.mark.asyncio
async def test_reservation_query_by_various_states():
    with PostgresContainer('postgres:16') as postgres:
        run('db_config.yaml', connection=postgres.get_connection_url())
        reservations = create_reservations(99)
        database = RelBase(conn_string=postgres.get_connection_url())
        opinions = LocalOpinionsProvider(MockedOpinionsDB(), None) #type: ignore
        for reservation in reservations:
            database.store_reservation(reservation)
        query = ReservationQuery(
            user="user_1",
            venue="venue_1",
            status=[Uncomfirmed().get_status()],
            limit=8
        )
        result = await query.query(database, opinions)
        for reservation in result.result:
            reservation.status = Accepted()
            database.update_reservation(reservation.persistance()) 
        result = await query.query(database, opinions)
        for reservation in result.result:
            reservation.status = Assisted()
            database.update_reservation(reservation.persistance())
        
        query_final = ReservationQuery(
            venue="venue_1",
            status=[Accepted().get_status(), Assisted().get_status()],
            limit=20
        )
        result = await query_final.query(database, opinions)
        accepted_result = list(filter(lambda x: x.status.get_status() == Accepted().get_status(),
                                 result.result))
        assisted_result = list(filter(lambda x: x.status.get_status() == Assisted().get_status(),
                                     result.result)) 
        assert result.total == 16
        assert len(accepted_result) == 8
        assert len(assisted_result) == 8
