from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from tg_stat_bot.constants import START_MESSAGE

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    """Handler for the start command."""
    await message.answer(text=START_MESSAGE)
