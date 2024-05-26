import pytest
import asyncio
import pytest_asyncio
import src.model.users.firebase.api_instance as fb
import src.model.users.firebase.exceptions as fe

@pytest.mark.asyncio
async def test_get_data():
   users = {
           "validToken": {
               "email": "valid@mail.com"
               }
           }
   firebase = fb.FirebaseMock(users)
   result = await firebase.get_data("validToken")
   assert result == users["validToken"]

@pytest.mark.asyncio
async def test_get_data_invalid():
    firebase = fb.FirebaseMock({})
    with pytest.raises(fe.InvalidToken):
       await firebase.get_data("invalidToken") 
