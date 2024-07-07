import pytest
from testcontainers.postgres import PostgresContainer
from src.model.venues.data.base import RelBase
from src.model.venues.venue import Available, create_venue
from src.model.venues.update import Update
from test.services.db_load import run
from src.model.venues.venueQuery import VenueQuery
from test.venues.test_query import all_different, create_venues

@pytest.mark.asyncio #TODO: DetachedInstanceError
async def test_venue_persistance():
    with PostgresContainer('postgres:16') as postgres:
        run('db_config.yaml', connection=postgres.get_connection_url()) 
        venue = create_venue(name="La Pizzerias", location="126 Main St", capacity=51)
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
        venue = create_venue(name="La Pizzerias", location="126 Main St", capacity=51)
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
                name="name_2",
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