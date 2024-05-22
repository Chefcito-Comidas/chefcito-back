from pydantic import BaseModel

from src.model.users.firebase.api_instance import FirebaseAuth
from src.model.users.permissions.base import Database
from src.model.users.permissions.schema import User

class UserData(BaseModel):
    localid: str
    email: str
    
    def allowed_to(self, endpoint: str, base: Database) -> bool:
        user = base.get_user(self.localid)
        return user != None and base.is_allowed(user, endpoint)

    def insert_into(self, user_type: str, base: Database) -> None:
        base.insert_user(User(uid=self.localid, email=self.email, user_type=user_type)) 

    def get_type(self, base: Database) -> str:
        user = base.get_user(self.localid)
        return User.check_anonymous(user).user_type 

def recover_data(token: str, auth: FirebaseAuth) -> 'UserData':
    data = auth.get_data(token)
    return UserData(localid=data['localId'],
                    email=data['email'])


