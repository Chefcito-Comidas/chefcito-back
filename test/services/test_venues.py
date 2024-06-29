import pytest
from testcontainers.postgres import PostgresContainer
from src.model.venues.data.base import RelBase
from src.model.venues.venue import Available, create_venue
from src.model.venues.update import Update
from test.services.db_load import run


@pytest.mark.asyncio
async def test_venue_persistance():
    with PostgresContainer('postgres:16') as postgres:
        run('db_config.yaml', connection=postgres.get_connection_url()) 
        venue = create_venue(name="La Pizzerias", location="126 Main St", capacity=51)
        database = RelBase(conn_string=postgres.get_connection_url())
        venue_with_id=venue.persistance()
        database.store_venue(venue_with_id)
        result = database.get_venue_by_id(venue_with_id.id)
        assert result != None
        assert result.id == venue_with_id.id

# @pytest.mark.asyncio
# async def test_venue_update():
#     with PostgresContainer('postgres:16') as postgres:
#         run('db_config.yaml', connection=postgres.get_connection_url()) 
#         venue = create_venue(name="La Pizzerias", location="126 Main St", capacity=51)
#         database = RelBase(conn_string=postgres.get_connection_url())
#         venue_with_id=venue.persistance()
#         database.store_venue(venue_with_id)
#         update = Update(name="La Pizzeria Updated")
#         venue = update.modify(venue)
#         venue_with_id=venue.persistance()
#         database.update_venue(venue_with_id)
#         result = database.get_venue_by_id(venue_with_id.id)
#         assert result != None
#         assert result.name == "La Pizzeria Updated"
