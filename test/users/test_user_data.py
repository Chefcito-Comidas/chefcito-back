import pytest
import asyncio
import src.model.users.permissions.base as pb
import src.model.users.user_data as ud
import src.model.users.firebase.api_instance as fb

def get_mocked_base() -> pb.Database:
    mocked_base = {
            'users': {
                'user_1': 'restaurant',
                'user_2': 'client',
                'super_user': 'restaurant',
                'another_nice_user': 'restaurant',
                'user_3': 'client'
                },
            'permissions': {
                'restaurant:/restaurant-allowed': True,
                'client:/client-allowed': True,
                'restaurant:/both-allowed': True,
                'client:/both-allowed': True,
                'anonymous:/all-allowed': True,
                'restaurant:/all-allowed': True,
                'client:/all-allowed': True
                }
            }
    return pb.DBMock(mocked_base)

def get_mocked_auth() -> fb.FirebaseAuth:
    mocked_clients = {
            'user_1': {
                'email': 'user1@mail.com',
                'localId': 'user_1'
                },
            'user_2': {
                'email': 'user2@mail.com',
                'localId': 'user_2'
                },
            'user_3': {
                'email': 'user3@mail.com',
                'localId': 'user_3'
                },
            'super_user': {
                'email': 'superduper@mail.com',
                'localId': 'super_user'
                },
            'another_nice_user': {
                'email': 'greatmail@mail.com',
                'localId': 'another_nice_user'
                },
            'user_not_in_base': {
                'email': 'newhere@mail.com',
                'localId': 'user_not_in_base'
                }
            }
    return fb.FirebaseMock(mocked_clients)

@pytest.mark.asyncio
async def test_unregistered_user_is_anonymous():
    data = ud.UserData(localid='someId', email='mail@mail.com')
    db = get_mocked_base()
    assert data.get_type(db) == 'anonymous'

@pytest.mark.asyncio
async def test_registered_user_is_not_anonymous():
   auth = get_mocked_auth()
   db = get_mocked_base()
   data = await ud.recover_data('user_1', auth)
   assert data.get_type(db) != 'anonymous'

@pytest.mark.asyncio
async def test_registering_a_new_valid_user_makes_it_no_longer_anonymous():
    auth = get_mocked_auth()
    db = get_mocked_base()
    data = await ud.recover_data('user_not_in_base', auth)
    assert data.get_type(db) == 'anonymous'
    data.insert_into('client', db)
    assert data.get_type(db) == 'client'

@pytest.mark.asyncio
async def test_anonymous_user_canot_call_a_non_anonymous_endpoint():
    db = get_mocked_base()
    auth = get_mocked_auth()
    data = await ud.recover_data('user_not_in_base', auth)
    
    assert not data.allowed_to('/restaurant-allowed', db)
    assert not data.allowed_to('/client-allowed', db)
    assert not data.allowed_to('/both-allowed', db)

@pytest.mark.asyncio
async def test_client_user_canot_call_restaurant_endpoint():
    db = get_mocked_base()
    auth = get_mocked_auth()
    data = await ud.recover_data('user_2', auth)

    assert not data.allowed_to('/restaurant-allowed', db)

@pytest.mark.asyncio
async def test_restaurant_user_cannot_call_client_endpoint():
    db = get_mocked_base()
    auth = get_mocked_auth()
    data = await ud.recover_data('user_1', auth)

    assert not data.allowed_to('/client-allowed', db)

@pytest.mark.asyncio
async def test_all_allowed_to_anonymous_endpoints():
    db = get_mocked_base()
    auth = get_mocked_auth()
    client = await ud.recover_data('user_2', auth)
    restaurant = await ud.recover_data('user_1', auth)
    anonymous = await ud.recover_data('user_not_in_base', auth)

    assert client.allowed_to('/all-allowed', db)
    assert restaurant.allowed_to('/all-allowed', db)
    assert anonymous.allowed_to('/all-allowed', db)
   
@pytest.mark.asyncio
async def test_client_and_restaurant_can_call_both_endpoint():
    db = get_mocked_base()
    auth = get_mocked_auth()
    client = await ud.recover_data('user_2', auth)
    restaurant = await ud.recover_data('user_1', auth)
    
    assert client.allowed_to('/both-allowed', db)
    assert restaurant.allowed_to('/both-allowed', db)


    
