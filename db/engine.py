import os
from datetime import datetime, timedelta

import pytz
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from db.models import Base, Answer
from sqlalchemy import select, update, func


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
            session.add(Answer(up='None', down='None', how_morning='None', how_night='None', tg_id=tg_id, amount='ОШИБКА! Какое-то поле не заполнено'))
            await session.commit()

async def set_up(up, tg_id):
    async with session_maker() as session:
        existing_record = await session.execute(
            select(Answer).where(Answer.tg_id == tg_id, func.date(Answer.created) == func.current_date())
        )
        record = existing_record.scalar()

        if record:
            # Если запись существует, обновляем поле 'up'
            query = update(Answer).where(Answer.tg_id == tg_id, func.date(Answer.created) == func.current_date()).values(up=up)
            await session.execute(query)
        else:
            # Если записи нет, создаем новую
            new_record = Answer(up=up, tg_id=tg_id, created=func.current_date())
            session.add(new_record)
        await session.commit()

async def set_down(down, tg_id):
    async with session_maker() as session:
        existing_record = await session.execute(
            select(Answer).where(Answer.tg_id == tg_id, func.date(Answer.created) == func.current_date())
        )
        record = existing_record.scalar()

        if record:
            # Если запись существует, обновляем поле 'up'
            query = update(Answer).where(Answer.tg_id == tg_id, func.date(Answer.created) == func.current_date()).values(down=down)
            await session.execute(query)
        else:
            # Если записи нет, создаем новую
            new_record = Answer(down=down, tg_id=tg_id, created=func.current_date())
            session.add(new_record)
        await session.commit()

async def set_how(how_morning, tg_id):
    async with session_maker() as session:
        existing_record = await session.execute(
            select(Answer).where(Answer.tg_id == tg_id, func.date(Answer.created) == func.current_date())
        )
        record = existing_record.scalar()

        if record:
            # Если запись существует, обновляем поле
            query = update(Answer).where(Answer.tg_id == tg_id).values(how_morning=how_morning)
            await session.execute(query)
        else:
            # Если записи нет, создаем новую
            new_record = Answer(how_morning=how_morning, tg_id=tg_id, created=func.current_date())
            session.add(new_record)
        await session.commit()

async def set_how_night(input_user, tg_id):
    async with session_maker() as session:
        existing_record = await session.execute(
            select(Answer).where(Answer.tg_id == tg_id, func.date(Answer.created) == func.current_date())
        )
        record = existing_record.scalar()

        if record:
            # Если запись существует, обновляем поле
            query = update(Answer).where(Answer.tg_id == tg_id).values(how_night=input_user)
            await session.execute(query)
        else:
            # Если записи нет, создаем новую
            new_record = Answer(how_night=input_user, tg_id=tg_id, created=func.current_date())
            session.add(new_record)
        await session.commit()


async def calculate_sleep_amount(tg_id):
    async with session_maker() as session:
        # Получение текущей даты
        current_date = datetime.now().date()

        query = select(Answer).where(
            Answer.tg_id == tg_id,
            func.date(Answer.created) == current_date
        )
        result = await session.execute(query)
        answer_instance = result.scalars().first()

        if answer_instance:
            up_time_str = answer_instance.up
            down_time_str = answer_instance.down

            # Проверка на наличие значений в полях 'up' и 'down'
            if not up_time_str or not down_time_str:
                # Если одно из полей не заполнено, устанавливаем 'amount' как "заполни меня"
                answer_update = update(Answer).where(
                    Answer.tg_id == tg_id,
                    func.date(Answer.created) == func.current_date()
                ).values(amount='ОШИБКА! Какое-то из полей не заполненно')
                await session.execute(answer_update)
            else:
                try:
                    # Преобразование строк в объекты времени
                    up_time = datetime.strptime(up_time_str, '%H:%M').time()
                    down_time = datetime.strptime(down_time_str, '%H:%M').time()

                    # Вычисление продолжительности сна
                    sleep_duration = calculate_duration(up_time, down_time)

                    # Преобразование продолжительности сна в часы
                    hours = int(sleep_duration.total_seconds() // 3600)
                    minutes = int((sleep_duration.total_seconds() % 3600) // 60)

                    formatted_sleep_duration = f"{hours} час {minutes} минут"

                    # Обновление записи в базе данных
                    answer_update = update(Answer).where(
                        Answer.tg_id == tg_id,
                        func.date(Answer.created) == func.current_date()
                    ).values(amount=formatted_sleep_duration)
                    await session.execute(answer_update)

                except ValueError as e:
                    # Обработка ошибки преобразования времени
                    # Здесь можно добавить логику для обработки ошибки
                    pass

            await session.commit()

def calculate_duration(up_time, down_time):
    # Получение времени как timedelta
    up_time_delta = timedelta(hours=up_time.hour, minutes=up_time.minute)
    down_time_delta = timedelta(hours=down_time.hour, minutes=down_time.minute)
    all_time_delta = timedelta(hours=24)

    # Вычисление разницы во времени
    if up_time < down_time:
        # Если up_time меньше down_time, это означает, что пользователь лёг спать и проснулся в тот же день
        return all_time_delta - (down_time_delta - up_time_delta)
    else:
        # Если up_time больше down_time, это означает, что пользователь лёг спать после полуночи и проснулся в следующий день
        return timedelta(days=1) - (up_time_delta - down_time_delta)

async def click_set_up(up, tg_id):
    async with session_maker() as session:
        # Преобразуем время нажатия в формат, подходящий для базы данных
        up_time = up.strftime('%H:%M')

        existing_record = await session.execute(
            select(Answer).where(Answer.tg_id == tg_id, func.date(Answer.created) == func.current_date())
        )
        record = existing_record.scalar()

        if record:
            # Если запись существует, обновляем поле 'up'
            query = update(Answer).where(Answer.tg_id == tg_id, func.date(Answer.created) == func.current_date()).values(up=up_time)
            await session.execute(query)
        else:
            # Если записи нет, создаем новую
            new_record = Answer(up=up_time, tg_id=tg_id, created=func.current_date())
            session.add(new_record)
        await session.commit()

async def fetch_all(tg_id: int):
    async with session_maker() as session:
        result = await session.execute(
            select(Answer).where(Answer.tg_id == tg_id))
        answers = result.scalars().all()
    return answers

async def click_set_down(down, tg_id):
    async with session_maker() as session:
        down_time = down.strftime('%H:%M')

        existing_record = await session.execute(
            select(Answer).where(Answer.tg_id == tg_id, func.date(Answer.created) == func.current_date())
        )
        record = existing_record.scalar()

        if record:
            query = update(Answer).where(Answer.tg_id == tg_id, func.date(Answer.created) == func.current_date()).values(down=down_time)
            await session.execute(query)
        else:
            new_record = Answer(down=down_time, tg_id=tg_id, created=func.current_date())
            session.add(new_record)
        await session.commit()

async def set_how_morning(input_user, tg_id):
    async with session_maker() as session:
        existing_record = await session.execute(
            select(Answer).where(Answer.tg_id == tg_id, func.date(Answer.created) == func.current_date())
        )
        record = existing_record.scalar()
        if record:
            query = update(Answer).where(Answer.tg_id == tg_id, func.date(Answer.created) == func.current_date()).values(how_morning=input_user)
            await session.execute(query)
        else:
            new_record = Answer(how_morning=input_user, tg_id=tg_id, created=func.current_date())
            session.add(new_record)
        await session.commit()

async def drop_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)