import asyncio
import os
from dotenv import load_dotenv
import logging
import sys

from aiogram import Bot, Dispatcher

from database.models import async_main


dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)


async def main():
    await async_main()
    bot: Bot = Bot(token=os.environ['BOT_TOKEN'])
    from telegram.handlers import router
    dp: Dispatcher = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Это конец, брат, бот закрыт.')
