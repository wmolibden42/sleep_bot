import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from db.models import Base, Answer
from sqlalchemy import select, update

#engine = create_async_engine(os.environ.get('DB_URL'), echo=True)
engine = create_async_engine(url='sqlite+aiosqlite:///db.sqlite3')
session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def set_user(tg_id):
    async with session_maker() as session:
        user = await session.scalar(select(Answer).where(Answer.tg_id == tg_id))

        if not user:
            session.add(Answer(up='Заполни меня', down='Заполни меня', how='Заполни меня', tg_id=tg_id))
            await session.commit()

async def set_up(up, tg_id):
    async with session_maker() as session:
        query = update(Answer).where(Answer.tg_id == tg_id).values(up=up,)
        await session.execute(query)
        await session.commit()

async def set_down(down, tg_id):
    async with session_maker() as session:
        query = update(Answer).where(Answer.tg_id == tg_id).values(down=down,)
        await session.execute(query)
        await session.commit()

async def set_how(how, tg_id):
    async with session_maker() as session:
        query = update(Answer).where(Answer.tg_id == tg_id).values(how=how,)
        await session.execute(query)
        await session.commit()

#async def amount():
#    async with session_maker() as session:
#        query = select(Answer.amount).where(Answer.tg_id == tg_id)
#        for row in session.query(Answer).all():
#            up = row.up
#            down = row.down

async def stat_all(tg_id):
    async with session_maker() as session:
        query = select(Answer).where(Answer.tg_id == tg_id)
        result = await session.execute(query)
        return result.scalars().all()

async def drop_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)