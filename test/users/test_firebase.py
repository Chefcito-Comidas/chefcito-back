import pytest
import src.model.users.firebase.api_instance as fb
import src.model.users.firebase.exceptions as fe

def test_get_data():
   users = {
           "validToken": {
               "email": "valid@mail.com"
               }
           }
   firebase = fb.FirebaseMock(users)
   result = firebase.get_data("validToken")
   assert result == users["validToken"]

def test_get_data_invalid():
    firebase = fb.FirebaseMock({})
    with pytest.raises(fe.InvalidToken):
       firebase.get_data("invalidToken") 
