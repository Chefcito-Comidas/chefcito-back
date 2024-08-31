from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class CommsSchema(DeclarativeBase):
    pass

class UserSchema(CommsSchema):
    __tablename__ = "numbers"

    id: Mapped[str] = mapped_column(primary_key=True)
    number: Mapped[str] = mapped_column()

    def __repr__(self) -> str:
        return f"{self.id}-{self.number}"