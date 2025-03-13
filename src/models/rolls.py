from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from src.database import Base
from datetime import date


class RollModel(Base):
    __tablename__ = "rolls"

    id: Mapped[int] = mapped_column(primary_key=True)
    length: Mapped[float]
    weight: Mapped[float]
    date_create: Mapped[date]
    date_delete: Mapped[date | None]