import asyncio
import logging
import sys
#from os import getenv
import os
from app.handlers import r
import db.engine as db

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())


async def main() -> None:
    token = os.environ.get("BOT_TOKEN")
    # All handlers should be attached to the Router (or Dispatcher)
    dp = Dispatcher()
    await db.create_db()
    bot = Bot(token, parse_mode=ParseMode.HTML)
    # And the run events dispatching
    dp.include_router(r)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())