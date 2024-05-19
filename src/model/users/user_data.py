from pydantic import BaseModel

from src.model.users.firebase.api_instance import FirebaseAuth


class UserData(BaseModel):
    localid: str
    email: str
    


def recover_data(token: str, auth: FirebaseAuth) -> 'UserData':
    data = auth.get_data(token)
    return UserData(localid=data['localId'],
                    email=data['email'])
