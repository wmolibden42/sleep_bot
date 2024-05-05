from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
     created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
     updated: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

class User(Base):
     __tablename__ = 'user'

     id: Mapped[str] = mapped_column(primary_key=True, autoincrement=True)
     name: Mapped[str] = mapped_column(String(20), nullable=False)
     