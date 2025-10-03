import asyncio
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

from content.constants import MIN_RATING_INT, MAX_RATING_INT
from content.models import Category, ContentFile, ContentRating, Topic
from tg_bot.constants import (
    BACK_BTN,
    CONTENT_HEADER,
    ERROR_MSG,
    FILE_LOADING_MSG,
    LEVEL_TEXTS,
    NEXT_PAGE_BTN,
    RATING_REPLY_MSG,
    SEARCH_HINT_MSG,
    SEARCH_NOT_FOUND_MSG,
    SEARCH_REPEAT_BTN,
    SEARCH_RESULTS_MSG,
    TOPIC_NAME_FORMAT,
    PREVIOUS_PAGE_BTN,
    TO_DESCRIPTION_BTN
)
from users.models import BotUser


router = Router()


async def get_category(category_id: int) -> Category:
    """Fetch a Category object by ID."""
    return await sync_to_async(Category.objects.get)(id=category_id)


async def get_topic_name(topic_id: int | None) -> str:
    """Get formatted topic name or empty string if no topic."""
    if topic_id:
        topic = await sync_to_async(Topic.objects.get)(id=topic_id)
        return TOPIC_NAME_FORMAT.format(topic.name)
    return ''


async def get_content_header(category_id: int, topic_id: int | None) -> str:
    """Generate content menu header."""
    category = await get_category(category_id)
    topic_name = await get_topic_name(topic_id)
    return CONTENT_HEADER.format(category.name, topic_name)


async def edit_message(
    callback: CallbackQuery,
    text: str,
    markup: InlineKeyboardBuilder | None = None,
    parse_mode: str = 'HTML'
):
    """Edit message with text and optional markup."""
    await callback.message.edit_text(
        text=text,
        reply_markup=markup if markup else None,
        parse_mode=parse_mode
    )
    await callback.answer()


async def send_media_file(
    query: CallbackQuery,
    content_item_id: int,
    level1: int,
    level2: int,
    level3: int | None,
    bot: Bot
):
    """Display media and a Back button."""
    media_data = await kb.get_media_file_data(content_item_id)
    if 'error' in media_data:
        await query.message.edit_text(ERROR_MSG.format(media_data['error']))
        return
    markup = await kb.get_media_back_keyboard(
        level1, level2, level3, content_item_id
    )
    try:
        file = FSInputFile(media_data['file_path'])
        caption = f'<b>{media_data.get('title', 'Медиафайл')}</b>'
        if media_data['content_type'] == 'IMAGE':
            await bot.send_photo(
                chat_id=query.from_user.id,
                photo=file,
                caption=caption,
                reply_markup=markup,
                parse_mode='HTML'
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
    """Handler for the start command. Representation for Level 1 buttons."""
    await message.answer(
        LEVEL_TEXTS['level1'],
        reply_markup=await kb.get_level1_menu(),
        parse_mode='HTML'
    )
    await message.delete()


@router.callback_query(cb.Level1Callback.filter())
async def handle_level1(
    callback: CallbackQuery,
    callback_data: cb.Level1Callback
):
    """Handler for Level 1 buttons. Representation for Level 2 buttons."""
    await edit_message(
        callback,
        text=LEVEL_TEXTS['level2'],
        markup=await kb.get_level2_menu(level1_choice=callback_data.choice)
    )


@router.callback_query(cb.PaginateLevel2Callback.filter())
async def handle_paginate_level2(
    callback: CallbackQuery,
    callback_data: cb.PaginateLevel2Callback
):
    """Handler for Level 1 buttons. Pagination for Level 2 buttons."""
    await edit_message(
        callback,
        text=LEVEL_TEXTS['level2'],
        markup=await kb.get_level2_menu(
            level1_choice=callback_data.level1,
            page=callback_data.page
        )
    )


@router.callback_query(cb.Level2Callback.filter())
async def handle_level2(
    callback: CallbackQuery,
    callback_data: cb.Level2Callback
):
    """Handler for Level 2 buttons. Representation for Level 3 buttons."""
    category = await get_category(callback_data.category)
    text = LEVEL_TEXTS['level3'].format(category.name)
    await edit_message(
        callback,
        text=text,
        markup=await kb.get_level3_menu(
            level1_choice=callback_data.level1,
            level2_choice=callback_data.category
        )
    )


@router.callback_query(cb.PaginateLevel3Callback.filter())
async def handle_paginate_level3(
    callback: CallbackQuery,
    callback_data: cb.PaginateLevel3Callback
):
    """Handler for Level 2 buttons. Pagination for Level 3 buttons."""
    category = await get_category(callback_data.level2)
    text = LEVEL_TEXTS['level3'].format(category.name)
    await edit_message(
        callback,
        text=text,
        markup=await kb.get_level3_menu(
            level1_choice=callback_data.level1,
            level2_choice=callback_data.level2,
            page=callback_data.page
        )
    )


@router.callback_query(cb.Level3Callback.filter())
async def handle_level3(
    callback: CallbackQuery,
    callback_data: cb.Level3Callback
):
    """Handler for Level 3 buttons. Representation for the content list."""
    text = await get_content_header(callback_data.level2, callback_data.topic)
    await edit_message(
        callback,
        text=text,
        markup=await kb.get_content_menu(
            level1_choice=callback_data.level1,
            level2_choice=callback_data.level2,
            level3_choice=callback_data.topic
        )
    )


@router.callback_query(cb.PaginateContentCallback.filter())
async def handle_paginate_content(
    callback: CallbackQuery,
    callback_data: cb.PaginateContentCallback
):
    """Handler for Level 3 buttons. Pagination for content."""
    text = await get_content_header(callback_data.level2, callback_data.level3)
    await edit_message(
        callback,
        text=text,
        markup=await kb.get_content_menu(
            level1_choice=callback_data.level1,
            level2_choice=callback_data.level2,
            level3_choice=callback_data.level3,
            page=callback_data.page
        )
    )


@router.callback_query(cb.BackLevel1Callback.filter())
async def handle_back_level1(callback: CallbackQuery):
    await edit_message(
        callback,
        text=LEVEL_TEXTS['level1'],
        markup=await kb.get_level1_menu()
    )


@router.callback_query(cb.BackLevel2Callback.filter())
async def handle_back_level2(
    callback: CallbackQuery,
    callback_data: cb.BackLevel2Callback
):
    await edit_message(
        callback,
        text=LEVEL_TEXTS['level2'],
        markup=await kb.get_level2_menu(level1_choice=callback_data.level1)
    )


@router.callback_query(cb.BackLevel3Callback.filter())
async def handle_back_level3(
    callback: CallbackQuery,
    callback_data: cb.BackLevel3Callback
):
    category = await get_category(callback_data.level2)
    text = LEVEL_TEXTS['level3'].format(category.name)
    await edit_message(
        callback,
        text=text,
        markup=await kb.get_level3_menu(
            level1_choice=callback_data.level1,
            level2_choice=callback_data.level2
        )
    )


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
        await edit_message(query, text=text, markup=markup)
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
    await edit_message(query, text=text, markup=markup)


@router.callback_query(cb.ContentMediaCallback.filter())
async def content_media_handler(
    query: CallbackQuery,
    callback_data: cb.ContentMediaCallback,
    bot: Bot
):
    """Handler for media files."""
    loading_message = await query.message.answer(FILE_LOADING_MSG)
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
    text = await get_content_header(callback_data.level2, callback_data.level3)
    markup = await kb.get_content_menu(
        callback_data.level1,
        callback_data.level2,
        callback_data.level3
    )
    await edit_message(query, text=text, markup=markup)


@router.callback_query(cb.SearchCallback.filter())
async def search_callback_handler(
    query: CallbackQuery,
    callback_data: cb.SearchCallback,
    state: FSMContext,
):
    """Handle search button click."""
    prompt_message = await query.message.edit_text(
        text=SEARCH_HINT_MSG,
        reply_markup=None,
        parse_mode='HTML'
    )
    await state.set_state(SearchState.waiting_for_query)
    await state.update_data(
        level1=callback_data.level1,
        level2=callback_data.level2,
        level3=callback_data.level3,
        prompt_message_id=prompt_message.message_id
    )
    await query.answer()


class SearchState(StatesGroup):
    waiting_for_query = State()


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
        files__paths__id=level1_choice,
        files__categories__id=level2_choice
    ).exists())() if level2_choice else False
    builder = InlineKeyboardBuilder()
    if level3_choice:
        back_callback = cb.Level3Callback(
            level1=level1_choice,
            level2=level2_choice,
            topic=level3_choice
        )
    elif level2_choice and not has_topics:
        back_callback = cb.Level3Callback(
            level1=level1_choice,
            level2=level2_choice,
            topic=0
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
            text=SEARCH_REPEAT_BTN,
            callback_data=cb.SearchCallback(
                level1=level1_choice,
                level2=level2_choice,
                level3=level3_choice
            ).pack()
        ))
        builder.add(InlineKeyboardButton(
            text=BACK_BTN,
            callback_data=back_callback.pack()
        ))
        builder.adjust(1)
        await message.answer(
            text=SEARCH_NOT_FOUND_MSG,
            reply_markup=builder.as_markup(),
            parse_mode='HTML'
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
                    level2=level2_choice or 0,
                    level3=level3_choice or 0,
                    content_item=item['id']
                ).pack()
            )
        )
    builder.adjust(1)
    if paginator.num_pages > 1:
        pagination_row = []
        if current_page.has_previous():
            pagination_row.append(InlineKeyboardButton(
                text=PREVIOUS_PAGE_BTN,
                callback_data=cb.PaginateContentCallback(
                    level1=level1_choice,
                    level2=level2_choice or 0,
                    level3=level3_choice or 0,
                    page=current_page.previous_page_number()
                ).pack()
            ))
        pagination_row.append(InlineKeyboardButton(
            text=f'{current_page.number}/{paginator.num_pages}',
            callback_data='no_action'
        ))
        if current_page.has_next():
            pagination_row.append(InlineKeyboardButton(
                text=NEXT_PAGE_BTN,
                callback_data=cb.PaginateContentCallback(
                    level1=level1_choice,
                    level2=level2_choice or 0,
                    level3=level3_choice or 0,
                    page=current_page.next_page_number()
                ).pack()
            ))
        builder.row(*pagination_row)
    builder.row(InlineKeyboardButton(
        text=SEARCH_REPEAT_BTN,
        callback_data=cb.SearchCallback(
            level1=level1_choice,
            level2=level2_choice,
            level3=level3_choice
        ).pack()
    ))
    builder.row(InlineKeyboardButton(
        text=BACK_BTN,
        callback_data=back_callback.pack()
    ))
    await message.answer(
        text=SEARCH_RESULTS_MSG.format(search_query),
        reply_markup=builder.as_markup(),
        parse_mode='HTML'
    )
    await state.clear()


class RatingState(StatesGroup):
    waiting_for_rating = State()


@router.callback_query(cb.RateCallback.filter())
async def start_rating(
    query: CallbackQuery,
    callback_data: cb.RateCallback,
    state: FSMContext
):
    """Show rating buttons."""
    builder = InlineKeyboardBuilder()
    for r in range(MIN_RATING_INT, MAX_RATING_INT + 1):
        builder.add(
            InlineKeyboardButton(
                text=str(r),
                callback_data=cb.RateSubmitCallback(
                    content_id=callback_data.content_id,
                    rating=r,
                    level1=callback_data.level1,
                    level2=callback_data.level2,
                    level3=callback_data.level3,
                ).pack()
            )
        )
    builder.adjust(MAX_RATING_INT)
    is_text_page = any(
        button.text == PREVIOUS_PAGE_BTN
        or button.text == NEXT_PAGE_BTN
        or button.text == TO_DESCRIPTION_BTN
        for row in query.message.reply_markup.inline_keyboard for button in row
    )
    await query.message.edit_reply_markup(reply_markup=builder.as_markup())
    await state.set_state(RatingState.waiting_for_rating)
    await state.update_data(
        content_id=callback_data.content_id,
        is_text_page=is_text_page,
        page=callback_data.page
    )
    await query.answer()


@router.callback_query(cb.RateSubmitCallback.filter())
async def submit_rating(
    query: CallbackQuery,
    callback_data: cb.RateSubmitCallback,
    state: FSMContext,
    bot: Bot
):
    """Save the rating and return to the previous keyboard."""
    user = await sync_to_async(
        BotUser.objects.get
    )(telegram_id=query.from_user.id)
    await sync_to_async(ContentRating.objects.update_or_create)(
        content_id=callback_data.content_id,
        user=user,
        defaults={'rating': callback_data.rating}
    )
    rating_reply_msg = await query.message.answer(
        RATING_REPLY_MSG,
        parse_mode='HTML'
    )
    is_media = (
        query.message.video or
        query.message.photo or
        query.message.document or
        query.message.audio
    )
    if is_media:
        markup = await kb.get_media_back_keyboard(
            callback_data.level1,
            callback_data.level2,
            callback_data.level3,
            callback_data.content_id
        )
        await query.message.bot.edit_message_reply_markup(
            chat_id=query.message.chat.id,
            message_id=query.message.message_id,
            reply_markup=markup
        )
    else:
        state_data = await state.get_data()
        if state_data.get('is_text_page', False):
            text, markup = await kb.get_content_page(
                callback_data.level1,
                callback_data.level2,
                callback_data.level3,
                callback_data.content_id,
                state_data.get('page', 1)
            )
        else:
            text, markup = await kb.get_content_description(
                callback_data.level1,
                callback_data.level2,
                callback_data.level3,
                callback_data.content_id
            )
        await edit_message(query, text=text, markup=markup)
    await asyncio.sleep(5)
    await bot.delete_message(
        chat_id=query.message.chat.id,
        message_id=rating_reply_msg.message_id
    )
    await state.clear()
