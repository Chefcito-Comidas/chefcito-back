from typing import Optional
from pydantic import BaseModel

from src.model.users.firebase.api_instance import FirebaseAuth
from src.model.users.permissions.base import Database
from src.model.users.permissions.schema import AssociatedData, User
from src.model.users.update import UserUpdate

# TODO: How we name this token should be configurable
ANONYMOUS_TOKEN = 'anonymous'

class UserData(BaseModel):
    localid: str
    email: str
    name: str
    phone_number: str

    def allowed_to(self, endpoint: str, base: Database) -> bool:
        user, _ = base.get_user(self.localid)
        return user != None and base.is_allowed(user, endpoint)

    def insert_into(self, user_type: str, base: Database) -> None:
        base.insert_user(
            User(uid=self.localid, email=self.email, user_type=user_type),
            AssociatedData(uid=self.localid, name=self.name, phone_number=self.phone_number)) 

    def get_type(self, base: Database) -> str:
        user, _ = base.get_user(self.localid)
        return User.check_anonymous(user).user_type 
    
    async def update(self, update: UserUpdate, base: Database) -> None:
        await base.update_data(self.localid, update)
        if update.name:
            self.name = update.name
        if update.phone:
            self.phone_number = update.phone

class UserToken(BaseModel):
    id_token: str 
    
    async def get_data(self, firebase: FirebaseAuth, base: Database) -> 'UserData':
        """
        Tries to recover user data with the firebase authenticator provided
        Raise an exception if the user is invalid
        """
        return await recover_data(self.id_token, firebase, base) 
    

async def recover_data(token: str, auth: FirebaseAuth, base: Database) -> 'UserData':
    data = await auth.get_data(token)
    user, user_data = base.get_user(data['localId'])
    if not user:
        user = User(uid=data['localId'], email=data['email'])
    if not user_data:
        user_data = AssociatedData(name="", phone_number="")
    return UserData(localid=user.uid,
                    email=user.email,
                    name=user_data.name,
                    phone_number=user_data.phone_number
                    )


