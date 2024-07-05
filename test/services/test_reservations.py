from datetime import datetime
import pytest
from testcontainers.postgres import PostgresContainer
from src.model.reservations.data.base import RelBase
from src.model.reservations.reservation import Accepted, Reservation, create_reservation
from src.model.reservations.reservationQuery import ReservationQuery
from src.model.reservations.update import Update
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
        update = Update(user="venue", accept=True)
        reservation = update.modify(reservation)
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
        database = RelBase(conn_string=postgres.get_connection_url())
        for reservation in reservations:
            database.store_reservation(reservation)
        
        query = ReservationQuery(
                user="user_1",
                limit=5
                )
        result_1 = query.query(database)
        query.start=5
        result_2 = query.query(database)
        query.start=10
        result_3= query.query(database)
        assert len(result_1) == len(result_2) == len(result_3) == 5
        assert all_different(result_1, result_2)
        assert all_different(result_1, result_3)
        assert all_different(result_2, result_3)
