from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Update
from asgiref.sync import sync_to_async
from django.utils import timezone

from content.models import ContentFile, ContentViewStat
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


class ContentStatMiddleware(BaseMiddleware):
    """Middleware for content statistics."""

    async def __call__(
        self,
        handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        result = await handler(event, data)
        await self.process_callback(event, data)
        return result

    async def process_callback(
        self,
        callback_query: CallbackQuery,
        data: Dict[str, Any]
    ):
        try:
            callback_data = data.get("callback_data")

            if not callback_data:
                return

            callback_type = type(callback_data).__name__
            target_callbacks = ['ContentReadCallback', 'ContentMediaCallback']

            if callback_type in target_callbacks:
                if hasattr(
                    callback_data,
                    'content_item'
                ) and callback_data.content_item:
                    if callback_type == 'ContentReadCallback':
                        if hasattr(
                            callback_data,
                            'page'
                        ) and callback_data.page != 1:
                            return

                    await self.record_content_stat(
                        callback_query.from_user,
                        callback_data.content_item,
                        callback_type
                    )
        except Exception as e:
            print(f"Ошибка в ContentStatMiddleware: {e}")

    @sync_to_async
    def record_content_stat(self, tg_user, content_item_id, callback_type):
        try:
            user = BotUser.objects.get(telegram_id=tg_user.id)
            content_file = ContentFile.objects.get(id=content_item_id)
            ContentViewStat.objects.create(
                user=user,
                content_file=content_file,
            )
        except Exception as e:
            print(f"Ошибка записи статистики: {e}")
