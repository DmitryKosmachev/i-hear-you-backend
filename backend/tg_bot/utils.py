import asyncio

from datetime import datetime, timedelta
from aiogram import Bot
from asgiref.sync import sync_to_async

from tg_bot.constants import INACTIVE_DAYS_FOR_MESSAGE, NOTIFICATION_PERIOD
from users.models import BotUser


async def send_reminders(bot: Bot):
    """The function of sending messages to inactive users."""
    while True:
        try:
            inactive_days_ago = (
                datetime.now() - timedelta(days=INACTIVE_DAYS_FOR_MESSAGE)
            )

            inactive_users = await sync_to_async(list)(
                BotUser.objects.filter(
                    last_active__lte=inactive_days_ago,
                    is_active=True)
            )

            for user in inactive_users:
                today = datetime.now().date()
                days_inactive = (today - user.last_active.date()).days
                if days_inactive % INACTIVE_DAYS_FOR_MESSAGE == 0:
                    await bot.send_message(
                        chat_id=user.telegram_id,
                        text="Мы по вам скучаем! Загляните к нам, у нас много нового 😊"
                    )
            await asyncio.sleep(NOTIFICATION_PERIOD)

        except Exception as e:
            print(f'Ошибка при отправке уведомлений: {e}')
