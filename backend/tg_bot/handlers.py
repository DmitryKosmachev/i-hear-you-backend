from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart

import tg_bot.keyboards as kb
import tg_bot.callbacks as cb


router = Router()


LEVEL_TEXTS = {
    "level1": "Выберите, для кого выбираем:",
    "level2": "Выберите категорию:",
    "level3": "Выберите тему:"
}


@router.message(CommandStart())
async def cmd_start(message: Message):
    """Обработчик команды старт. Представление кнопок 1 уровня."""
    await message.answer(
        "Добро пожаловать! Выбирете для кого ищете контент.",
        reply_markup=await kb.get_level1_menu()
    )


@router.callback_query(cb.Level1Callback.filter())
async def handle_level1(
    callback: CallbackQuery,
    callback_data: cb.Level1Callback
):
    """Обработчик кнопок 1 уровня меню. Представление кнопок 2 уровня."""
    text = LEVEL_TEXTS['level2']
    await callback.message.edit_text(
        text,
        reply_markup=await kb.get_level2_menu(level1_choice=callback_data.choice)
    )
    await callback.answer()


@router.callback_query(cb.PaginateLevel2Callback.filter())
async def handle_paginate_level2(
    callback: CallbackQuery,
    callback_data: cb.PaginateLevel2Callback
):
    """Обработчик кнопок 1 уровня. Пагинация кнопок 2 уровня."""
    await callback.message.edit_text(
        text="Уровень 2",
        reply_markup=await kb.get_level2_menu(
            level1_choice=callback_data.level1,
            page=callback_data.page
        )
    )
    await callback.answer()


@router.callback_query(cb.Level2Callback.filter())
async def handle_level2(
    callback: CallbackQuery,
    callback_data: cb.Level2Callback
):
    """Обработчик кнопок 2 уровня меню. Представление кнопок 3 уровня."""
    text = LEVEL_TEXTS['level3']
    await callback.message.edit_text(
        text,
        reply_markup=await kb.get_level3_menu(
            level1_choice=callback_data.level1,
            level2_choice=callback_data.category)
    )
    await callback.answer()


@router.callback_query(cb.PaginateLevel3Callback.filter())
async def handle_paginate_level3(
    callback: CallbackQuery,
    callback_data: cb.PaginateLevel3Callback
):
    """Обработчик кнопок 2 уровня меню. Пагинация кнопок уровня 3."""
    await callback.message.edit_text(
        text=LEVEL_TEXTS['level3'],
        reply_markup=await kb.get_level3_menu(
            level1_choice=callback_data.level1,
            level2_choice=callback_data.level2,
            page=callback_data.page
        )
    )
    await callback.answer()


@router.callback_query(cb.Level3Callback.filter())
async def handle_level3(
    callback: CallbackQuery,
    callback_data: cb.Level3Callback
):
    """Обработчик кнопок 3 уровня меню. Представление списка контента."""
    await callback.message.edit_text(
        text='Контент',
        reply_markup=await kb.get_content_menu(
            level1_choice=callback_data.level1,
            level2_choice=callback_data.level2,
            level3_choice=callback_data.topic,
        )
    )
    await callback.answer()


@router.callback_query(cb.PaginateContentCallback.filter())
async def handle_paginate_content(
    callback: CallbackQuery,
    callback_data: cb.PaginateContentCallback
):
    """Обработчик кнопок 3 уровня меню. Пагинация контента."""
    await callback.message.edit_text(
        text="Контент",
        reply_markup=await kb.get_content_menu(
            level1_choice=callback_data.level1,
            level2_choice=callback_data.level2,
            level3_choice=callback_data.level3,
            page=callback_data.page
        )
    )
    await callback.answer()


@router.callback_query(cb.ContentChoiceCallback.filter())
async def handle_content_choice(
    callback: CallbackQuery,
    callback_data: cb.ContentChoiceCallback
):
    await callback.message.edit_text(
        text=f"Контент: {callback_data.content_item}",
        reply_markup=await kb.get_text_keyboard(
            level1_choice=callback_data.level1,
            level2_choice=callback_data.level2,
            level3_choice=callback_data.level3
        )
    )
    await callback.answer()


@router.callback_query(cb.BackLevel1Callback.filter())
async def handle_back_level1(callback: CallbackQuery):
    await callback.message.edit_text(
        text="Стартовое меню",
        reply_markup=await kb.get_level1_menu()
    )
    await callback.answer()


@router.callback_query(cb.BackLevel2Callback.filter())
async def handle_back_level2(
    callback: CallbackQuery,
    callback_data: cb.BackLevel2Callback
):
    await callback.message.edit_text(
        text="Уровень 2",
        reply_markup=await kb.get_level2_menu(level1_choice=callback_data.level1)
    )
    await callback.answer()


@router.callback_query(cb.BackLevel3Callback.filter())
async def handle_back_level3(
    callback: CallbackQuery,
    callback_data: cb.BackLevel3Callback
):
    await callback.message.edit_text(
        text="Уровень 3",
        reply_markup=kb.get_level3_menu(
            level1_choice=callback_data.level1,
            level2_choice=callback_data.level2
        )
    )
    await callback.answer()


@router.callback_query(cb.BackContentCallback.filter())
async def handle_back_content(
    callback: CallbackQuery,
    callback_data: cb.BackContentCallback
):
    await callback.message.edit_text(
        text="Контент",
        reply_markup=kb.get_content_menu(
            level1_choice=callback_data.level1,
            level2_choice=callback_data.level2,
            level3_choice=callback_data.level3
        )
    )
    await callback.answer()
