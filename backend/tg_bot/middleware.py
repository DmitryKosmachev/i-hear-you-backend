from aiogram import BaseMiddleware
from aiogram.types import Update
from asgiref.sync import sync_to_async
from django.utils import timezone

from users.models import BotUser


class UserActivityMiddleware(BaseMiddleware):
    """Register new users and keep them active."""

    async def __call__(self, handler, event: Update, data: dict):
        user = None
        if event.message:
            user = event.message.from_user
        elif event.callback_query:
            user = event.callback_query.from_user
        if user:
            await self.create_or_update_user(user)
        return await handler(event, data)

    @sync_to_async
    def create_or_update_user(self, tg_user):
        """Creates or updates a user."""
        try:
            user, created = BotUser.objects.get_or_create(
                telegram_id=tg_user.id,
                defaults={
                    'username': tg_user.username or '',
                    'first_name': tg_user.first_name or '',
                    'last_active': timezone.now(),
                    'is_active': True
                }
            )
            if not created:
                user.last_active = timezone.now()
                if user.first_name != (tg_user.first_name or ''):
                    user.first_name = tg_user.first_name or ''
                if user.username != (tg_user.username or ''):
                    user.username = tg_user.username or ''
                user.save()
            return user

        except Exception:
            return None
