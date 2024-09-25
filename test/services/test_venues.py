import pytest
from testcontainers.postgres import PostgresContainer
from src.model.venues.data.base import RelBase
from src.model.venues.venue import Available, create_venue, Venue
from src.model.venues.update import Update
from test.services.db_load import run
from src.model.venues.venueQuery import VenueQuery
from test.venues.test_query import all_different, create_venues
from datetime import datetime

@pytest.mark.asyncio 
async def test_venue_persistance():
    with PostgresContainer('postgres:16') as postgres:
        run('db_config.yaml', connection=postgres.get_connection_url()) 
        venue = create_venue(name="La Pizzerias", location="126 Main St", capacity=51, logo="foto.url", pictures = ["foto1", "foto2"], slots=[datetime.now()], characteristics= ["Arepas", "Cafeteria"], vacations=[datetime.now()], reservationLeadTime=10,menu="comidas.url")
        database = RelBase(conn_string=postgres.get_connection_url())
        venue_with_id=venue.persistance()
        database.store_venue(venue_with_id)
        result = database.get_venue_by_id(venue.id)
        assert result != None
        assert result.id == venue.id

@pytest.mark.asyncio
async def test_venue_update():
    with PostgresContainer('postgres:16') as postgres:
        run('db_config.yaml', connection=postgres.get_connection_url()) 
        venue = create_venue(name="La Pizzerias", location="126 Main St", capacity=51, logo="foto.url", pictures = ["foto1", "foto2"],slots=[datetime.now(),datetime.now()], characteristics= ["Arepas", "Cafeteria"], vacations=[datetime.now()], reservationLeadTime=10,menu="comidas.url")
        database = RelBase(conn_string=postgres.get_connection_url())
        venue_with_id=venue.persistance()
        database.store_venue(venue_with_id)
        update = Update(name="La Pizzeria Updated")
        venue = update.modify(venue)
        venue_with_id=venue.persistance()
        database.update_venue(venue_with_id)
        result = database.get_venue_by_id(venue_with_id.id)
        assert result != None
        assert result.id == venue_with_id.id
        assert result.name == "La Pizzeria Updated"
        


@pytest.mark.asyncio
async def test_venue_pagination():
    with PostgresContainer('postgres:16') as postgres:
        run('db_config.yaml', connection=postgres.get_connection_url()) 
        venues = create_venues(99) 
        database = RelBase(conn_string=postgres.get_connection_url())
        for venue in venues:
            database.store_venue(venue)

        query = VenueQuery(
                limit=5
                )
        result_1 = query.query(database)
        query.start=5
        result_2 = query.query(database)
        query.start=10
        result_3= query.query(database)
        assert result_1.total == result_2.total == result_3.total == 99
        assert len(result_1.result) == len(result_2.result) == len(result_3.result) == 5
        assert all_different(result_1.result, result_2.result)
        assert all_different(result_1.result, result_3.result)
        assert all_different(result_2.result, result_3.result)

@pytest.mark.asyncio
async def test_venue_deletion():
    with PostgresContainer('postgres:16') as postgres:
        run('db_config.yaml', connection=postgres.get_connection_url()) 
        venue = create_venue("La Pizzerias", "126 Main St", 51, logo="foto.url", pictures = ["foto1", "foto2"], slots=[datetime.now()], characteristics= ["hamburgueseria", "pizzeria"], vacations=[datetime.now()], reservationLeadTime=10,menu="comidas.url")
        database = RelBase(conn_string=postgres.get_connection_url())
        database.store_venue(venue.persistance())
        assert database.get_venue_by_id(venue.id) != None
        Venue.delete(venue.id, database)
        assert database.get_venue_by_id(venue.id) == None

@pytest.mark.asyncio
async def test_venue_filter():
    with PostgresContainer('postgres:16') as postgres:
        run('db_config.yaml', connection=postgres.get_connection_url()) 
        venues = create_venues(99) 
        database = RelBase(conn_string=postgres.get_connection_url())
        for venue in venues:
            database.store_venue(venue)

        query = VenueQuery(
                name="name_1",
                characteristics=["charact1_1"],
                
                )
        result_1 = query.query(database)
        
        assert result_1.total ==  33
        
        