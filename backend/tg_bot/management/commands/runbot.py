import asyncio
import logging

from aiogram import Bot, Dispatcher
from django.core.management.base import BaseCommand
from django.conf import settings

from tg_bot.handlers import router


class Command(BaseCommand):
    help = 'Start the Telegram bot'

    def add_arguments(self, parser):
        parser.add_argument(
            '--token',
            type=str,
            help='Telegram bot token (takes priority over variables)',
        )

    def handle(self, *args, **options):
        logging.basicConfig(level=logging.INFO)

        token = (options.get('token') or settings.TELEGRAM_BOT_TOKEN)

        if not token:
            self.stderr.write(
                self.style.ERROR(
                    '❌ Bot token not found. '
                    'Enter token using one of the methods:\n'
                    '   - Command argument --token <token>\n'
                    '   - Via enviromental variable TELEGRAM_BOT_TOKEN'
                )
            )
            return

        self.stdout.write(
            self.style.SUCCESS(f'Starting bot with token: {token[:10]}...')
        )

        try:
            asyncio.run(self.main(token))
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING('🛑 Aborted by user'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'❌ Error: {e}'))

    async def main(self, token):
        bot = Bot(token=token)
        dp = Dispatcher()
        dp.include_router(router)

        self.stdout.write(self.style.SUCCESS('✅ Bot started!'))

        await dp.start_polling(bot)
