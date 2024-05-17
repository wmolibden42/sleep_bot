import asyncio
import logging
import sys
#from os import getenv
import os
from datetime import datetime, timedelta
from random import random

from aiogram.types import Message

from app.handlers import r
import db.engine as db

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode

from dotenv import load_dotenv, find_dotenv

from db.models import Answer

load_dotenv(find_dotenv())


#async def send_message(chat_id, text):
   # await bot.send_message(chat_id, text)


async def daily_mailing(message: Message):
    async with db.session_maker() as session:
        # Получите текущее время
        now = datetime.now()
        print(f"Текущее время: {now}")

        user_ids = session.query(Answer.tg_id).all()
        print(f"Список ID пользователей: {user_ids}")

        # Утренний диапазон времени от 8 до 10 утра
        morning_start = now.replace(hour=8, minute=0, second=0, microsecond=0)
        morning_end = now.replace(hour=10, minute=0, second=0, microsecond=0)

        # Вечерний диапазон времени от 20 до 22 часов
        evening_start = now.replace(hour=17, minute=50, second=0, microsecond=0)
        evening_end = now.replace(hour=18, minute=0, second=0, microsecond=0)

        # Отправка утренних сообщений
        if morning_start <= now <= morning_end:
            for chat_id in user_ids:
                await message.answer(chat_id, "Привет! Не забудь записать время подъема")
                await asyncio.sleep(random.randint(5, 10))  # Случайная задержка

        # Отправка вечерних сообщений
        elif evening_start <= now <= evening_end:
            for chat_id in user_ids:
                await message.answer(chat_id, "Привет! Не забывай зафиксировать время отбоя")
             #   await asyncio.sleep(random.randint(5, 10))  # Случайная задержка

async def scheduler():
    # Планирование задачи на 9 утра и 9 вечера каждый день
    while True:
        await daily_mailing()
        await asyncio.sleep(3600)  # Проверка каждый час

async def main() -> None:
    token = os.environ.get("BOT_TOKEN")
    # All handlers should be attached to the Router (or Dispatcher)
    dp = Dispatcher()
    await db.create_db()
    bot = Bot(token, parse_mode=ParseMode.HTML)
    # And the run events dispatching
    dp.include_router(r)
    await dp.start_polling(bot)
    dp.loop.create_task(scheduler())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
