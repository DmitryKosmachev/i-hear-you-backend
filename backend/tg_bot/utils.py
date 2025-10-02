from datetime import timedelta

import asyncio
from aiogram import Bot
from asgiref.sync import sync_to_async
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone

from tg_bot import keyboards as kb
from tg_bot.constants import (
    DEFAULT_REMINDER_MESSAGE,
    INACTIVE_DAYS_FOR_MESSAGE,
    NOTIFICATION_PERIOD,
)
from tg_bot.models import BotMessage
from users.models import BotUser


async def send_reminders(bot: Bot):
    """The function of sending messages to inactive users."""
    while True:
        try:
            inactive_days_ago = (
                timezone.now() - timedelta(days=INACTIVE_DAYS_FOR_MESSAGE)
            )
            inactive_users = await sync_to_async(list)(
                BotUser.objects.filter(
                    last_active__lte=inactive_days_ago,
                    is_active=True)
            )

            try:
                reminder_message = await BotMessage.objects.aget(
                    key='reminder_message'
                )
                message_text = reminder_message.text
            except ObjectDoesNotExist:
                message_text = DEFAULT_REMINDER_MESSAGE

            for user in inactive_users:
                today = timezone.now().date()
                days_inactive = (today - user.last_active.date()).days
                if days_inactive % INACTIVE_DAYS_FOR_MESSAGE == 0:
                    await bot.send_message(
                        chat_id=user.telegram_id,
                        text=message_text,
                        reply_markup=await kb.get_level1_menu()
                    )
            await asyncio.sleep(NOTIFICATION_PERIOD)

        except Exception as e:
            print(f'Ошибка при отправке уведомлений: {e}')
            await asyncio.sleep(NOTIFICATION_PERIOD)
