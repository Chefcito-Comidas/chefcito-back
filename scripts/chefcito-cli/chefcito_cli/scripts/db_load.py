from datetime import datetime
from typing import List
from sqlalchemy import create_engine, delete, insert, update
from sqlalchemy.orm import Session
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import Column, String, Integer, ARRAY, DateTime
from sqlalchemy import ForeignKey, UniqueConstraint
import yaml

TYPES_KEY = 'usertypes'
ENDPOINTS_KEY = 'endpoints'

ANONYMOUS_KEY = 'anonymous'
CLIENT_KEY = 'client'
RESTAURANT_KEY = 'restaurant'

ENDPOINT_NAME = 'name'
ENDPOINT_PERMISSIONS = 'allowed'

class Base(DeclarativeBase):
    pass


class VenueSchema(Base):

    __tablename__ = "venues"

    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    location: Mapped[str] = mapped_column()
    capacity: Mapped[int] = mapped_column()
    logo: Mapped[str] = mapped_column()
    pictures: Mapped[List[str]] = mapped_column(ARRAY(String))
    slots: Mapped[List[datetime]] = mapped_column(ARRAY(DateTime))
    characteristics: Mapped[List[str]] = mapped_column(ARRAY(String))
    vacations: Mapped[List[datetime]] = mapped_column(ARRAY(DateTime))
    reservationLeadTime: Mapped[int] = mapped_column()
    status: Mapped[str] = mapped_column()
    
    def __repr__(self) -> str:
        return (f"Venue(id={self.id}, name={self.name}, location={self.location}, "
                f"capacity={self.capacity}, "
                f"logo={self.logo}, pictures={self.pictures}, slots={self.slots}), "
                f"characteristics={self.characteristics}), vacations={self.vacations}), "
                f"reservationLeadTime={self.reservationLeadTime}), status={self.status}")


class ReservationSchema(Base):
    __tablename__ = "reservations"

    id: Mapped[str] = mapped_column(primary_key=True)
    user: Mapped[str] = mapped_column()
    venue: Mapped[str] = mapped_column()
    time: Mapped[datetime] = mapped_column()
    people: Mapped[int] = mapped_column()
    status: Mapped[str] = mapped_column()

    def __repr__(self) -> str:
        return f"{self.id}:{self.user}:{self.venue}/at:{self.time}/for:{self.people}/{self.status}"
 
class UserType(Base):
    __tablename__ = "user_types"

    type: Mapped[str] = mapped_column(primary_key=True)

    def __repr__(self) -> str:
        return f"{self.type}"

class User(Base):
    __tablename__ = "users"

    uid: Mapped[str] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(UniqueConstraint())
    user_type: Mapped[str] = mapped_column(ForeignKey("user_types.type"))

    def __repr__(self) -> str:
        return f"{self.user_type} user: {self.email} => {self.uid}"

class Permission(Base):
   __tablename__ = "permissions"

   user_type: Mapped[str] = mapped_column(ForeignKey("user_types.type"), primary_key=True)
   endpoint: Mapped[str] = mapped_column(primary_key=True)

   def __repr__(self) -> str:
       return f"{self.user_type} ==> {self.endpoint}"

def generate_user_types(yaml_config: dict) -> dict[str, str]:
    types = {}
    types[ANONYMOUS_KEY] = yaml_config.get(TYPES_KEY, {}).get(ANONYMOUS_KEY, ANONYMOUS_KEY)
    types[CLIENT_KEY] = yaml_config.get(TYPES_KEY, {}).get(CLIENT_KEY, CLIENT_KEY)
    types[RESTAURANT_KEY] = yaml_config.get(TYPES_KEY, {}).get(RESTAURANT_KEY, RESTAURANT_KEY)

    return types

def get_allowed_types(allowances: list[str], types: dict[str, str]) -> list[str]:
    if len(allowances) == 1 and types[ANONYMOUS_KEY] in allowances:
        return list(types.values())
    result = []
    for allowance in allowances:
        if not allowance in types.values():
            raise Exception(f"Invalid given type: {allowance}")
        result.append(allowance)
    return result

def generate_permissions(yaml_config: dict, types: dict[str, str]) -> list[Permission]:
    endpoints: list[dict] = yaml_config.get(ENDPOINTS_KEY, [])
    permissions = []
    for endpoint in endpoints:
        allowed_types: list[str] = get_allowed_types(endpoint[ENDPOINT_PERMISSIONS], types)
        for allowed_type in allowed_types:
            permission = Permission(endpoint=endpoint[ENDPOINT_NAME], user_type=allowed_type)
            permissions.append(permission)
    return permissions

def map_types(types: list[str]) -> list[UserType]:
    mapped = []
    for user_type in types:
        mapped.append(UserType(type=user_type))
    return mapped

def generate_user_configuration(config_file: str) -> tuple[list[UserType], list[Permission]]:
    with open(config_file, 'r+') as config:
        yaml_config = yaml.safe_load(config)
        types = generate_user_types(yaml_config) 
        permissions = generate_permissions(yaml_config, types)
    return map_types(list(types.values())), permissions 

def try_adding_user_types(types: List[UserType], session: Session) -> None:
    for value in types:
        try:
            insert_query = insert(UserType).values(type=value.type)
            session.execute(insert_query)
            session.commit()
        except Exception:
            session.rollback()
            print(f"{value.type} ==> Already in db")

def try_adding_permissions(permissions: List[Permission], session: Session):
    for permission in permissions:
        insert_query = insert(Permission).values(endpoint=permission.endpoint, 
                                                 user_type=permission.user_type)
        delete_query = delete(Permission).where(Permission.endpoint == permission.endpoint)
        try:
            session.execute(insert_query)
            session.commit()
        except Exception:
            session.rollback()
            session.execute(delete_query)
            session.execute(insert_query)
            session.commit()

def insert_data(types: list[UserType], permissions: list[Permission], conn_string: str):
    local_engine = create_engine(conn_string)
    Base.metadata.create_all(local_engine)
    with Session(local_engine) as session:
        try_adding_user_types(types, session)
        try_adding_permissions(permissions, session)

# TODO: allow this script to impact the real database
# TODO: add a second command to this script to update the schema instead of
# just brute forcing the data again
def run(config_file: str = "db_config.yaml", conn_string: str = "postgresql+psycopg2://user:admin123@localhost/users_db"):
    types, permissions = generate_user_configuration(config_file)
    insert_data(types, permissions, conn_string)

if __name__ == "__main__":
    run("db_config.yaml")
