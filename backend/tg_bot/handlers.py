from aiogram import Bot, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    FSInputFile,
    InlineKeyboardButton,
    Message
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from asgiref.sync import sync_to_async
from django.core.paginator import Paginator

import tg_bot.callbacks as cb
import tg_bot.keyboards as kb
from content.models import ContentFile, Topic


router = Router()

LEVEL_TEXTS = {
    'level1': (
        'Добро пожаловать! '
        'Пожалуйста, выберите, с каким запросом Вы к нам пришли:'
    ),
    'level2': 'Выберите категорию:',
    'level3': 'Выберите тему или нажмите "Показать все", '
    'чтобы показать все материалы в категории:'
}


class SearchState(StatesGroup):
    waiting_for_query = State()


async def send_media_file(
    query: CallbackQuery,
    content_item_id: str,
    level1: str,
    level2: str,
    level3: str,
    bot: Bot
):
    """Display media and a Back button."""
    media_data = await kb.get_media_file_data(content_item_id)
    if 'error' in media_data:
        await query.message.edit_text(f'Ошибка: {media_data["error"]}')
        return
    markup = await kb.get_media_back_keyboard(
        level1, level2, level3, content_item_id
    )
    try:
        file = FSInputFile(media_data['file_path'])
        caption = f'<b>{media_data.get("title", "Медиафайл")}</b>'
        if media_data['content_type'] == 'IMAGE':
            await bot.send_photo(
                chat_id=query.from_user.id,
                photo=file,
                caption=caption,
                reply_markup=markup,
                parse_mode="HTML"
            )
        elif media_data['content_type'] == 'VIDEO':
            await bot.send_video(
                chat_id=query.from_user.id,
                video=file,
                caption=caption,
                reply_markup=markup,
                parse_mode='HTML'
            )
        elif media_data['content_type'] == 'PDF':
            await bot.send_document(
                chat_id=query.from_user.id,
                document=file,
                caption=caption,
                reply_markup=markup,
                parse_mode='HTML'
            )
        elif media_data['content_type'] == 'AUDIO':
            await bot.send_audio(
                chat_id=query.from_user.id,
                audio=file,
                caption=caption,
                reply_markup=markup,
                parse_mode='HTML'
            )
        await query.answer('Материал отправлен!')
    except Exception as e:
        await query.message.edit_text(f'Ошибка отправки материала: {str(e)}')


@router.message(CommandStart())
async def cmd_start(message: Message):
    """Handler for the start command. Representaiton for Level 1 buttons."""
    await message.answer(
        LEVEL_TEXTS['level1'],
        reply_markup=await kb.get_level1_menu()
    )
    await message.delete()


@router.callback_query(cb.Level1Callback.filter())
async def handle_level1(
    callback: CallbackQuery,
    callback_data: cb.Level1Callback
):
    """"Handler for Level 1 buttons. Representation for Level 2 buttons."""
    text = LEVEL_TEXTS['level2']
    await callback.message.edit_text(
        text,
        reply_markup=await kb.get_level2_menu(
            level1_choice=callback_data.choice
        )
    )
    await callback.answer()


@router.callback_query(cb.PaginateLevel2Callback.filter())
async def handle_paginate_level2(
    callback: CallbackQuery,
    callback_data: cb.PaginateLevel2Callback
):
    """Handler for Level 1 buttons. Pagination for Level 2 buttons."""
    await callback.message.edit_text(
        text=LEVEL_TEXTS['level2'],
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
    """Handler for Level 2 buttons. Representation for Level 3 buttons."""
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
    """Handler for Level 2 buttons. Pagination for Level 3 buttons."""
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
    """Handler for Level 3 buttons. Representation for the content list."""
    await callback.message.edit_text(
        text='Материалы:',
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
    """Handler for Level 3 buttons. Pagination for content."""
    await callback.message.edit_text(
        text='Материалы:',
        reply_markup=await kb.get_content_menu(
            level1_choice=callback_data.level1,
            level2_choice=callback_data.level2,
            level3_choice=callback_data.level3,
            page=callback_data.page
        )
    )
    await callback.answer()


@router.callback_query(cb.BackLevel1Callback.filter())
async def handle_back_level1(callback: CallbackQuery):
    await callback.message.edit_text(
        text=LEVEL_TEXTS['level1'],
        reply_markup=await kb.get_level1_menu()
    )
    await callback.answer()


@router.callback_query(cb.BackLevel2Callback.filter())
async def handle_back_level2(
    callback: CallbackQuery,
    callback_data: cb.BackLevel2Callback
):
    await callback.message.edit_text(
        text=LEVEL_TEXTS['level2'],
        reply_markup=await kb.get_level2_menu(
            level1_choice=callback_data.level1
        )
    )
    await callback.answer()


@router.callback_query(cb.BackLevel3Callback.filter())
async def handle_back_level3(
    callback: CallbackQuery,
    callback_data: cb.BackLevel3Callback
):
    await callback.message.edit_text(
        text=LEVEL_TEXTS['level3'],
        reply_markup=await kb.get_level3_menu(
            level1_choice=callback_data.level1,
            level2_choice=callback_data.level2
        )
    )
    await callback.answer()


@router.callback_query(cb.ContentDescriptionCallback.filter())
async def content_description_handler(
    query: CallbackQuery,
    callback_data: cb.ContentDescriptionCallback
):
    """Handler for content description."""
    text, markup = await kb.get_content_description(
        callback_data.level1,
        callback_data.level2,
        callback_data.level3,
        callback_data.content_item
    )
    try:
        await query.message.edit_text(
            text,
            reply_markup=markup,
            parse_mode='HTML'
        )
    except Exception:
        await query.message.delete()
        await query.message.answer(
            text,
            reply_markup=markup,
            parse_mode='HTML'
        )


@router.callback_query(cb.ContentReadCallback.filter())
async def content_read_handler(
    query: CallbackQuery,
    callback_data: cb.ContentReadCallback
):
    text, markup = await kb.get_content_page(
        callback_data.level1,
        callback_data.level2,
        callback_data.level3,
        callback_data.content_item,
        callback_data.page
    )
    await query.message.edit_text(text, reply_markup=markup, parse_mode='HTML')


@router.callback_query(cb.ContentMediaCallback.filter())
async def content_media_handler(
    query: CallbackQuery,
    callback_data: cb.ContentMediaCallback,
    bot: Bot
):
    """Handler for media files."""
    loading_message = await query.message.answer('⏳ Файл загружается...')
    await query.message.delete()
    await send_media_file(
        query,
        callback_data.content_item,
        callback_data.level1,
        callback_data.level2,
        callback_data.level3,
        bot
    )
    await loading_message.delete()


@router.callback_query(cb.BackToContentListCallback.filter())
async def back_to_content_list_handler(
    query: CallbackQuery,
    callback_data: cb.BackToContentListCallback
):
    """Handler for the back-to-content-list button."""
    markup = await kb.get_content_menu(
        callback_data.level1,
        callback_data.level2,
        callback_data.level3
    )
    await query.message.edit_text('Материалы:', reply_markup=markup)


@router.callback_query(cb.SearchCallback.filter())
async def search_callback_handler(
    query: CallbackQuery,
    callback_data: cb.SearchCallback,
    state: FSMContext,
    bot: Bot
):
    """Handle search button click."""
    prompt_message = await query.message.edit_text(
        text='Введите запрос для поиска материала по названию:',
        reply_markup=None
    )
    await state.set_state(SearchState.waiting_for_query)
    await state.update_data(
        level1=callback_data.level1,
        level2=callback_data.level2,
        level3=callback_data.level3,
        prompt_message_id=prompt_message.message_id
    )
    await query.answer()


@router.message(SearchState.waiting_for_query)
async def process_search_query(
    message: Message,
    state: FSMContext,
    bot: Bot
):
    """Process search query and display results."""
    search_query = message.text.strip()
    state_data = await state.get_data()
    level1_choice = state_data.get('level1')
    level2_choice = state_data.get('level2')
    level3_choice = state_data.get('level3')
    prompt_message_id = state_data.get('prompt_message_id')
    if prompt_message_id:
        await bot.delete_message(
            chat_id=message.chat.id,
            message_id=prompt_message_id
        )
    await message.delete()
    filters = {
        'is_active': True,
        'name__icontains': search_query
    }
    content_items = await sync_to_async(list)(
        ContentFile.objects.filter(**filters).distinct().values('name', 'id')
    )
    has_topics = await sync_to_async(lambda: Topic.objects.filter(
        is_active=True,
        files__is_active=True,
        files__paths__slug=level1_choice,
        files__categories__slug=level2_choice
    ).exists())() if level2_choice else False
    builder = InlineKeyboardBuilder()
    if level3_choice and level3_choice != 'all':
        back_callback = cb.Level3Callback(
            level1=level1_choice,
            level2=level2_choice,
            topic=level3_choice
        )
    elif level2_choice and not has_topics:
        back_callback = cb.Level3Callback(
            level1=level1_choice,
            level2=level2_choice,
            topic='all'
        )
    elif level2_choice:
        back_callback = cb.Level2Callback(
            level1=level1_choice,
            category=level2_choice
        )
    else:
        back_callback = cb.Level1Callback(choice=level1_choice)
    if not content_items:
        builder.add(InlineKeyboardButton(
            text='🔍 Повторить поиск',
            callback_data=cb.SearchCallback(
                level1=level1_choice,
                level2=level2_choice,
                level3=level3_choice
            ).pack()
        ))
        builder.add(InlineKeyboardButton(
            text='⬅️ Назад',
            callback_data=back_callback.pack()
        ))
        builder.adjust(1)
        await message.answer(
            text='Материалы не найдены. Попробуйте другой запрос.',
            reply_markup=builder.as_markup()
        )
        await state.clear()
        return
    paginator = Paginator(content_items, kb.ITEMS_PER_PAGE)
    current_page = paginator.get_page(1)
    builder = InlineKeyboardBuilder()
    for item in current_page.object_list:
        builder.add(
            InlineKeyboardButton(
                text=item['name'],
                callback_data=cb.ContentDescriptionCallback(
                    level1=level1_choice,
                    level2=level2_choice or 'all',
                    level3=level3_choice or 'all',
                    content_item=item['id']
                ).pack()
            )
        )
    builder.adjust(1)
    if paginator.num_pages > 1:
        pagination_row = []
        if current_page.has_previous():
            pagination_row.append(InlineKeyboardButton(
                text="◀️",
                callback_data=cb.PaginateContentCallback(
                    level1=level1_choice,
                    level2=level2_choice or 'all',
                    level3=level3_choice or 'all',
                    page=current_page.previous_page_number()
                ).pack()
            ))
        pagination_row.append(InlineKeyboardButton(
            text=f'{current_page.number}/{paginator.num_pages}',
            callback_data='no_action'
        ))
        if current_page.has_next():
            pagination_row.append(InlineKeyboardButton(
                text="▶️",
                callback_data=cb.PaginateContentCallback(
                    level1=level1_choice,
                    level2=level2_choice or 'all',
                    level3=level3_choice or 'all',
                    page=current_page.next_page_number()
                ).pack()
            ))
        builder.row(*pagination_row)
    builder.row(InlineKeyboardButton(
        text='🔍 Повторить поиск',
        callback_data=cb.SearchCallback(
            level1=level1_choice,
            level2=level2_choice,
            level3=level3_choice
        ).pack()
    ))
    builder.row(InlineKeyboardButton(
        text='⬅️ Назад',
        callback_data=back_callback.pack()
    ))
    await message.answer(
        text=f'Результаты поиска для "{search_query}":',
        reply_markup=builder.as_markup()
    )
    await state.clear()
