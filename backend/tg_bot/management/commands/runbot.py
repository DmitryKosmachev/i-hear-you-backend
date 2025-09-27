# your_app/management/commands/runbot.py
import os
import asyncio
import logging
from django.core.management.base import BaseCommand
from django.conf import settings
from aiogram import Bot, Dispatcher
from tg_bot.handlers import router


class Command(BaseCommand):
    help = 'Запускает Telegram-бота'

    def add_arguments(self, parser):
        parser.add_argument(
            '--token',
            type=str,
            help='Telegram Bot Token (приоритет над настройками)',
        )

    def handle(self, *args, **options):
        logging.basicConfig(level=logging.INFO)

        token = (options.get('token') or
                 os.getenv('TG_TOKEN') or
                 getattr(settings, 'TELEGRAM_BOT_TOKEN', None))

        if not token:
            self.stderr.write(
                self.style.ERROR(
                    '❌ Токен бота не найден. Укажите одним из способов:\n'
                    '   - Через --token в командной строке\n'
                    '   - Через переменную окружения TG_TOKEN\n'
                    '   - Через настройку TELEGRAM_BOT_TOKEN в settings.py'
                )
            )
            return

        self.stdout.write(
            self.style.SUCCESS(f'Запуск бота с токеном: {token[:10]}...')
        )

        try:
            asyncio.run(self.main(token))
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('🛑 Остановлено пользователем'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'❌ Ошибка: {e}'))

    async def main(self, token):
        bot = Bot(token=token)
        dp = Dispatcher()
        dp.include_router(router)

        self.stdout.write(self.style.SUCCESS('✅ Бот запущен успешно!'))

        await dp.start_polling(bot)
