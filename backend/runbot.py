import asyncio
import logging

from aiogram import Bot, Dispatcher
from django.conf import settings

from tg_bot.handlers import router


async def main():
    bot = Bot(settings.TELEGRAM_BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
