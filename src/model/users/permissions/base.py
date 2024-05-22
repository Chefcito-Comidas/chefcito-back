from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from src.model.users.permissions.schema import User, Permission

DEFAULT_POOL_SIZE = 10

class Database():
    

    def get_user(self, uid: str) -> User | None:
        """
        Returns a user from the database
        """
        raise Exception("Interface method")

    def is_allowed(self, user: User, endpoint: str) -> bool:
        """
        Checks if a certain user is allowed to access an endpoint
        """
        raise Exception("Interface method")

    def insert_user(self, user: User) -> None:
        """
        Inserts a new user into the database
        """
        raise Exception("Interface method")

class DBEngine(Database):

    def __init__(self, conn_string: str, **kwargs):
        kwargs["pool_size"] = kwargs.get("pool_size", DEFAULT_POOL_SIZE)
        self.__engine = create_engine(conn_string, **kwargs)
    
    def get_user(self, uid: str) -> User | None:
        session = Session(self.__engine)
    
        user_query = select(User).where(User.uid.__eq__(uid))
        result = session.scalar(user_query)
        session.close()
        return result 
    
    def is_allowed(self, user: User, endpoint: str) -> bool:
        session = Session(self.__engine)
        """SELECT *
        FROM permissions
        JOIN users ON users.user_type = permissions.user_type
        WHERE permissions.endpoint = {endpoint} AND users.user_type = permissions.type"""
        authorization_query = select(Permission)\
                                .join(User.user_type)\
                                .where(Permission.endpoint.__eq__(endpoint))\
                                .where(Permission.user_type.__eq__(user.user_type))
                                
        result = session.scalar(authorization_query) != None
        session.close()
        return result
    
    def insert_user(self, user: User) -> None:
        session = Session(self.__engine)
        session.add(user)
        session.commit()
        session.close()


class DBMock(Database):
   
    def __init__(self, base_mock: dict[str, dict[str, str]]) -> None:
       self.base = base_mock

    def get_user(self, uid: str) -> User | None:
        user_type = self.base.get('users', {}).get(uid, 'anonymous')
        if user_type:
           return User(uid=uid, email="testmail@user.com", user_type=user_type) 

        return None 
    
    def  is_allowed(self, user: User, endpoint: str) -> bool:
        
        return self.base.get('permissions', {}).get(f"{user.user_type}:{endpoint}", None) != None

    def insert_user(self, user: User) -> None:
        users = self.base.get('users', {})
        users[user.uid] = user.user_type
        self.base['users'] = users
