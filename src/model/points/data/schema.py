from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class PointsBaseSchema(DeclarativeBase):
    pass

class PointSchema(PointsBaseSchema):

    __tablename__ = "points"

    total: Mapped[int] = mapped_column()
    user: Mapped[str] = mapped_column(primary_key=True)