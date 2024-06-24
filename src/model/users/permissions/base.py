from sqlalchemy import BinaryExpression, Column, create_engine, select
from sqlalchemy.orm import Session
from src.model.users.permissions.schema import User, Permission

# TODO: This pool size makes more sense if it is configurable
DEFAULT_POOL_SIZE = 10

class Database():
    
    def __add_param_at(self, endpoint: str, position: int = -1) -> str:
        splitted = endpoint.split("/")
        splitted[position] = "param"
        return "/".join(splitted)

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
    
    def __get_condition(self, endpoint: str) -> BinaryExpression[bool]:
        endpoints = [endpoint, self.__add_param_at(endpoint)]
        return Permission.endpoint.in_(endpoints)

    def is_allowed(self, user: User, endpoint: str) -> bool:
        session = Session(self.__engine)
        """SELECT *
        FROM permissions
        JOIN users ON users.user_type = permissions.user_type
        WHERE permissions.endpoint = {endpoint} AND users.user_type = permissions.type"""
        authorization_query = select(Permission)\
                                .where(self.__get_condition(endpoint))\
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
    
    def __check_all(self, endpoint: str, user_type: str) -> bool:
        endpoints = [endpoint, self.__add_param_at(endpoint)]
        return any(
                map(lambda endpoint: self.base.get('permissions', {}).get(f"{user_type}:{endpoint}", None) != None,
                endpoints)
                )


    def  is_allowed(self, user: User, endpoint: str) -> bool:
        
        return self.__check_all(endpoint, user.user_type) 

    def insert_user(self, user: User) -> None:
        users = self.base.get('users', {})
        users[user.uid] = user.user_type
        self.base['users'] = users
