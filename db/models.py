from sqlalchemy import DateTime, String, func, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import BigInteger

class Base(DeclarativeBase):
     created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
     #updated: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class Answer(Base):
     __tablename__ = 'answers'

     id: Mapped[int] = mapped_column(primary_key=True)
     up: Mapped[int] = mapped_column(nullable=True)
     down: Mapped[int] = mapped_column(String(25), nullable=True)
     how_morning: Mapped[int] = mapped_column(String(120), nullable=True)
     how_night: Mapped[int] = mapped_column(String(120), nullable=True)
     tg_id: Mapped[BigInteger] = mapped_column(BigInteger)
     amount: Mapped[int] = mapped_column(nullable=True)
