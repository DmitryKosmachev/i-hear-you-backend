from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from tg_stat_bot.constants import START_MESSAGE
from tg_stat_bot.utils import send_start_stats


router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    """Handler for the start command."""
    text = START_MESSAGE + '\n' + await send_start_stats()
    await message.answer(text=text)
