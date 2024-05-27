from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import ForeignKey, UniqueConstraint

class Base(DeclarativeBase):
    pass

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

# TODO: move this to a config file
user_types = [
        UserType(type="registered"), 
        UserType(type="restaurant"),
        UserType(type="anonymous")
              ]

# TODO: move this to a config file
permissions = [
        Permission(user_type="registered", endpoint="/profile"),
        Permission(user_type="restaurant", endpoint="/menu"),
        Permission(user_type="anonymous", endpoint="/restaurants")
        ]

engine = create_engine("postgresql+psycopg2://user:admin123@localhost/users_db")

Base.metadata.create_all(engine)

with Session(engine) as session:
    session.add_all(user_types)
    session.commit()
    session.add_all(permissions)
    session.commit()
        
