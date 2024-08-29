from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import ForeignKey, UniqueConstraint
from typing import Self

ANONYMOUS_UID = 'anonymousUID'
ANONYMOUS_MAIL = 'anonymous@mail.com'
# TODO: type should be configurable 
ANONYMOUS_TYPE = 'anonymous'

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
    
    @classmethod
    def check_anonymous(cls, user: Self | None) -> 'User':
       return user if user != None else cls.get_anonymous() 
    
    @classmethod
    def get_anonymous(cls) -> 'User':
       return cls(uid=ANONYMOUS_UID, email=ANONYMOUS_MAIL, user_type=ANONYMOUS_TYPE)



class Permission(Base):
   __tablename__ = "permissions"

   user_type: Mapped[str] = mapped_column(ForeignKey("user_types.type"), primary_key=True)
   endpoint: Mapped[str] = mapped_column(primary_key=True)

   def __repr__(self) -> str:
       return f"{self.user_type} ==> {self.endpoint}"

class AssociatedData(Base):
    __tablename__ = "users_data"

    uid: Mapped[str] = mapped_column(ForeignKey("users.uid"),primary_key=True)
    name: Mapped[str] = mapped_column()
    phone_number: Mapped[str] = mapped_column()

    def __repr__(self) -> str:
        return f"{self.uid} => {self.name} => {self.phone_number}"