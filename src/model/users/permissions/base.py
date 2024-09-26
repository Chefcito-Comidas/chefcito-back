from typing import Tuple
from sqlalchemy import BinaryExpression, Column, create_engine, select
from sqlalchemy.orm import Session
from src.model.users.permissions.schema import AssociatedData, User, Permission
from src.model.users.update import UserUpdate

# TODO: This pool size makes more sense if it is configurable
DEFAULT_POOL_SIZE = 10

class Database():
    
    def _add_param_at(self, endpoint: str, position: int = -1) -> str:
        splitted = endpoint.split("/")
        splitted[position] = "param"
        return "/".join(splitted)

    def get_user(self, uid: str) -> Tuple[User | None, AssociatedData | None]:
        """
        Returns a user from the database
        """
        raise Exception("Interface method")

    def is_allowed(self, user: User, endpoint: str) -> bool:
        """
        Checks if a certain user is allowed to access an endpoint
        """
        raise Exception("Interface method")

    def insert_user(self, user: User, data: AssociatedData) -> None:
        """
        Inserts a new user into the database
        """
        raise Exception("Interface method")
    
    async def update_data(self, user: str, update: UserUpdate) -> None:
        """
            Updates user data based on the values present at update
        """
        raise Exception("Interface method should not be called")

class DBEngine(Database):

    def __init__(self, conn_string: str, **kwargs):
        super().__init__()
        kwargs["pool_size"] = kwargs.get("pool_size", DEFAULT_POOL_SIZE)
        self.__engine = create_engine(conn_string, **kwargs)
    
    def get_user(self, uid: str) -> Tuple[User | None,AssociatedData | None]:
        session = Session(self.__engine)
    
        user_query = select(User).where(User.uid.__eq__(uid))
        data_query = select(AssociatedData).where(AssociatedData.uid.__eq__(uid))
        result = session.scalar(user_query)
        data_result = session.scalar(data_query)
        session.close()
        return result,data_result 
    
    def __get_condition(self, endpoint: str) -> BinaryExpression[bool]:
        endpoints = [endpoint, super()._add_param_at(endpoint)]
        return Permission.endpoint.in_(endpoints)

    def is_allowed(self, user: User, endpoint: str) -> bool:
        session = Session(self.__engine)
        """SELECT *
        FROM permissions
        JOIN users ON users.user_type = permissions.user_type
        WHERE permissions.endpoint = {endpoint} AND users.user_type = permissions.type"""
        param_endpoint = endpoint.split("/")
        param_endpoint[-1] = 'param'
        param_endpoint = '/'.join(param_endpoint)
        authorization_query = select(Permission)\
                                .where(self.__get_condition(endpoint))\
                                .where(Permission.user_type.__eq__(user.user_type))
                                
        result = session.scalar(authorization_query) != None
        session.close()
        return result
    
    def insert_user(self, user: User, data: AssociatedData) -> None:
        session = Session(self.__engine)
        session.add(user)
        session.commit()
        session.add(data)
        session.commit()
        session.close()
    
    async def update_data(self, user: str, update: UserUpdate) -> None:
        session = Session(self.__engine)
        value = session.scalar(select(AssociatedData).where(AssociatedData.uid.__eq__(user)))
        if value and update.name:
            value.name = update.name
        if value and update.phone:
            value.phone_number = update.phone
        session.commit()
        session.close()

class DBMock(Database):
   
    def __init__(self, base_mock: dict[str, Tuple[User, AssociatedData]], permissions: dict[str, bool]) -> None:
       super().__init__()
       self.base = base_mock
       self.permissions = permissions

    def get_user(self, uid: str) -> Tuple[User | None, AssociatedData | None]:
        
        user_type = self.base.get(uid, None)
        if user_type:
           return user_type 

        return User(uid=uid, email="", user_type="anonymous"), None 
    
    def __check_all(self, endpoint: str, user_type: str) -> bool:
        endpoints = [endpoint, self._add_param_at(endpoint)]
        return any(
                map(lambda endpoint: self.permissions.get(f"{user_type}:{endpoint}", None) != None,
                endpoints)
                )


    def  is_allowed(self, user: User, endpoint: str) -> bool:
        
        return self.__check_all(endpoint, user.user_type) 

    def insert_user(self, user: User, data: AssociatedData) -> None:
        self.base[user.uid] = (user,data)
        
    async def update_data(self, user: str, update: UserUpdate) -> None:
        (user, data) = self.base.get(user, (None, None)) #type: ignore
        if data:
            if update.phone:
               data.phone_number = update.phone
            if update.name:
                data.name = update.name
            self.base[data.uid] = (user, data) #type: ignore
