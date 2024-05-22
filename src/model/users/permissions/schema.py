from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy import ForeignKey, UniqueConstraint
from typing import Self

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
       return user if user != None else cls(uid='', email='', user_type='anonymous') 

class Permission(Base):
   __tablename__ = "permissions"

   user_type: Mapped[str] = mapped_column(ForeignKey("user_types.type"), primary_key=True)
   endpoint: Mapped[str] = mapped_column(primary_key=True)

   def __repr__(self) -> str:
       return f"{self.user_type} ==> {self.endpoint}"

