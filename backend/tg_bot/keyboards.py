from asgiref.sync import sync_to_async
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from django.core.paginator import Paginator

import tg_bot.callbacks as cb
from content.models import Category, Theme, Type

ITEMS_PER_PAGE = 8
NUMBER_OF_KOLUMNS = 2

categories = [
    '1 к',
    '2 к',
    '3 к',
    '4 к',
    '8 к',
    '8 к',
    '8 к',
    '8 к',
    '8 к',
    '8 r',
    '8 к',
    '8 к',
    '8 к',
    '8 r',
]


async def get_level1_menu():
    """Стартовое меню. Данные загружаются из БД."""
    builder = InlineKeyboardBuilder()

    menu_items = await sync_to_async(list)(Type.objects.all().values('name', 'slug'))

    for item in menu_items:
        builder.add(InlineKeyboardButton(
            text=item['name'],
            callback_data=cb.Level1Callback(choice=item['slug']).pack()
        ))

    builder.adjust(2)
    return builder.as_markup()

@sync_to_async
def get_categories_page(level1_choice: str, page: int = 1, items_per_page: int = ITEMS_PER_PAGE):
    """Синхронная функция для получения страницы категорий"""
    categories = list(Category.objects.filter(is_active=True).values('name', 'slug'))
    paginator = Paginator(categories, items_per_page)
    current_page = paginator.get_page(page)

    return {
        'categories': list(current_page.object_list),
        'current_page': page,
        'num_pages': paginator.num_pages,
        'has_previous': current_page.has_previous(),
        'has_next': current_page.has_next(),
        'previous_page_number': current_page.previous_page_number() if current_page.has_previous() else None,
        'next_page_number': current_page.next_page_number() if current_page.has_next() else None,
        'level1_choice': level1_choice
    }


async def get_level2_menu(
    level1_choice: str,
    page: int = 1,
    items_per_page: int = ITEMS_PER_PAGE
):
    """Меню второго уровня. Категории."""
    builder = InlineKeyboardBuilder()
    page_data = await get_categories_page(level1_choice, page, items_per_page)
    categories = page_data['categories']

    for cat in categories:
        builder.add(InlineKeyboardButton(
            text=cat['name'],
            callback_data=cb.Level2Callback(
                level1=level1_choice,
                category=cat['slug'],
            ).pack()
        ))

    builder.adjust(NUMBER_OF_KOLUMNS)

    if page_data['num_pages'] > 1:
        pagination_row = []

        if page_data['has_previous']:
            pagination_row.append(InlineKeyboardButton(
                text="◀️",
                callback_data=cb.PaginateLevel2Callback(
                    level1=level1_choice,
                    page=page_data['previous_page_number']
                ).pack()
            ))

        pagination_row.append(InlineKeyboardButton(
            text=f"{page_data['current_page']}/{page_data['num_pages']}",
            callback_data="no_action"
        ))

        if page_data['has_next']:
            pagination_row.append(InlineKeyboardButton(
                text="▶️",
                callback_data=cb.PaginateLevel2Callback(
                    level1=level1_choice,
                    page=page_data['next_page_number']
                ).pack()
            ))

        builder.row(*pagination_row)

    builder.row(InlineKeyboardButton(
        text="⬅️ Назад",
        callback_data=cb.BackLevel1Callback().pack()
    ))

    return builder.as_markup()


@sync_to_async
def get_level3_menu_data(
    level2_choice: str,
    page: int = 1,
    items_per_page: int = ITEMS_PER_PAGE
):
    """Синхронная функция для получения данных меню третьего уровня"""
    topics = list(
        Theme.objects.filter(is_active=True).values('name', 'slug')
    )

    paginator = Paginator(topics, items_per_page)
    current_page = paginator.get_page(page)

    return {
        'topics': list(current_page.object_list),
        'current_page': page,
        'num_pages': paginator.num_pages,
        'has_previous': current_page.has_previous(),
        'has_next': current_page.has_next(),
        'previous_page_number': current_page.previous_page_number() if current_page.has_previous() else None,
        'next_page_number': current_page.next_page_number() if current_page.has_next() else None,
    }


async def get_level3_menu(
    level1_choice: str,
    level2_choice: str,
    page: int = 1,
    items_per_page: int = ITEMS_PER_PAGE
):
    """Меню третьего уровня. Темы."""
    builder = InlineKeyboardBuilder()

    page_data = await get_level3_menu_data(level2_choice, page, items_per_page)
    topics = page_data['topics']

    for topic in topics:
        builder.add(
            InlineKeyboardButton(
                text=topic['name'],
                callback_data=cb.Level3Callback(
                    level1=level1_choice,
                    level2=level2_choice,
                    topic=topic['slug']
                ).pack()
            )
        )
    builder.adjust(NUMBER_OF_KOLUMNS)

    if page_data['num_pages'] > 1:
        pagination_row = []
        if page_data['has_previous']:
            pagination_row.append(InlineKeyboardButton(
                text="◀️",
                callback_data=cb.PaginateLevel3Callback(
                    level1=level1_choice,
                    level2=level2_choice,
                    page=page_data['previous_page_number']
                ).pack()
            ))

        pagination_row.append(InlineKeyboardButton(
            text=f"{page_data['current_page']}/{page_data['num_pages']}",
            callback_data="no_action"
        ))

        if page_data['has_next']:
            pagination_row.append(InlineKeyboardButton(
                text="▶️",
                callback_data=cb.PaginateLevel3Callback(
                    level1=level1_choice,
                    level2=level2_choice,
                    page=page_data['next_page_number']
                ).pack()
            ))
        builder.row(*pagination_row)

    builder.row(InlineKeyboardButton(
        text="⬅️ Назад",
        callback_data=cb.BackLevel2Callback(level1=level1_choice).pack()
    ))

    return builder.as_markup()


def get_content_menu(
    level1_choice: str,
    level2_choice: str,
    level3_choice: str,
    page: int = 1,
    items_per_page: int = ITEMS_PER_PAGE
):
    """Меню контента."""
    builder = InlineKeyboardBuilder()
    paginator = Paginator(categories, items_per_page)
    current_page = paginator.get_page(page)

    for cat in current_page.object_list:
        builder.add(
            InlineKeyboardButton(
                text=cat,
                callback_data=cb.ContentChoiceCallback(
                    level1=level1_choice,
                    level2=level2_choice,
                    level3=level3_choice,
                    content_item=cat
                ).pack()
            )
        )
    builder.adjust(NUMBER_OF_KOLUMNS)

    if current_page.has_other_pages():
        pagination_row = []
        if current_page.has_previous():
            prev_page = current_page.previous_page_number()
            pagination_row.append(InlineKeyboardButton(
                text="◀️",
                callback_data=cb.PaginateContentCallback(
                    level1=level1_choice,
                    level2=level2_choice,
                    level3=level3_choice,
                    page=prev_page
                ).pack()
            ))

        pagination_row.append(InlineKeyboardButton(
            text=f"{page}/{paginator.num_pages}",
            callback_data="no_action"
        ))

        if current_page.has_next():
            next_page = current_page.next_page_number()
            pagination_row.append(InlineKeyboardButton(
                text="▶️",
                callback_data=cb.PaginateContentCallback(
                    level1=level1_choice,
                    level2=level2_choice,
                    level3=level3_choice,
                    page=next_page
                ).pack()
            ))
        builder.row(*pagination_row)

    builder.row(InlineKeyboardButton(
        text="⬅️ Назад",
        callback_data=cb.BackLevel3Callback(
            level1=level1_choice,
            level2=level2_choice
        ).pack()
    ))

    return builder.as_markup()


def get_text_keyboard(
    level1_choice: str,
    level2_choice: str,
    level3_choice: str
):
    """Клавиатура для текстового контента."""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="⬅️ Назад",
        callback_data=cb.BackContentCallback(
            level1=level1_choice,
            level2=level2_choice,
            level3=level3_choice
        ).pack()
    ))
    return builder.as_markup()
