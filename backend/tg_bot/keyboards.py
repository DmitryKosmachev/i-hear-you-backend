import os

from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from asgiref.sync import sync_to_async
from django.core.paginator import Paginator

import tg_bot.callbacks as cb
from content.models import Category, ContentFile, Path, Topic


ITEMS_PER_PAGE = 8
NUMBER_OF_COLUMNS = 2


async def get_level1_menu():
    """Start menu (path). Load data from the database."""
    builder = InlineKeyboardBuilder()
    menu_items = await sync_to_async(list)(
        Path.objects.all().values('name', 'slug')
    )

    for item in menu_items:
        builder.add(
            InlineKeyboardButton(
                text=item['name'],
                callback_data=cb.Level1Callback(choice=item['slug']).pack()
            )
        )

    builder.adjust(NUMBER_OF_COLUMNS)
    return builder.as_markup()


@sync_to_async
def get_categories_page(
    level1_choice: str,
    page: int = 1,
    items_per_page: int = ITEMS_PER_PAGE
):
    """Get a page with categories."""
    categories = Category.objects.filter(
        is_active=True,
        files__is_active=True,
        files__paths__slug=level1_choice
        ).distinct().values('name', 'slug')
    paginator = Paginator(categories, items_per_page)
    current_page = paginator.get_page(page)

    return {
        'categories': list(current_page.object_list),
        'current_page': page,
        'num_pages': paginator.num_pages,
        'has_previous': current_page.has_previous(),
        'has_next': current_page.has_next(),
        'previous_page_number': (
            current_page.previous_page_number()
            if current_page.has_previous()
            else None
        ),
        'next_page_number': (
            current_page.next_page_number()
            if current_page.has_next()
            else None
        ),
        'level1_choice': level1_choice
    }


async def get_level2_menu(
    level1_choice: str,
    page: int = 1,
    items_per_page: int = ITEMS_PER_PAGE
):
    """Level 2 menu. Categories."""
    builder = InlineKeyboardBuilder()
    page_data = await get_categories_page(level1_choice, page, items_per_page)
    categories = page_data['categories']

    for cat in categories:
        has_topics = await sync_to_async(
            lambda: Topic.objects.filter(
                is_active=True,
                files__is_active=True,
                files__paths__slug=level1_choice,
                files__categories__slug=cat['slug']
            ).exists()
        )()
        callback_data = (
            cb.Level3Callback(
                level1=level1_choice,
                level2=cat['slug'],
                topic="all"
            )
            if not has_topics
            else cb.Level2Callback(level1=level1_choice, category=cat['slug'])
        )
        builder.add(
            InlineKeyboardButton(
                text=cat['name'],
                callback_data=callback_data.pack()
            )
        )

    builder.adjust(NUMBER_OF_COLUMNS)

    if page_data['num_pages'] > 1:
        pagination_row = []

        if page_data['has_previous']:
            pagination_row.append(InlineKeyboardButton(
                text='◀️',
                callback_data=cb.PaginateLevel2Callback(
                    level1=level1_choice,
                    page=page_data['previous_page_number']
                ).pack()
            ))

        pagination_row.append(InlineKeyboardButton(
            text=f'{page_data["current_page"]}/{page_data["num_pages"]}',
            callback_data='no_action'
        ))

        if page_data['has_next']:
            pagination_row.append(InlineKeyboardButton(
                text='▶️',
                callback_data=cb.PaginateLevel2Callback(
                    level1=level1_choice,
                    page=page_data['next_page_number']
                ).pack()
            ))

        builder.row(*pagination_row)

    builder.row(InlineKeyboardButton(
        text='⬅️ Назад',
        callback_data=cb.BackLevel1Callback().pack()
    ))

    return builder.as_markup()


@sync_to_async
def get_level3_menu_data(
    level1_choice: str,
    level2_choice: str,
    page: int = 1,
    items_per_page: int = ITEMS_PER_PAGE
):
    """Get data for the Level 3 menu (topics)."""
    topics = Topic.objects.filter(
        is_active=True,
        files__is_active=True,
        files__paths__slug=level1_choice,
        files__categories__slug=level2_choice,
        ).distinct().values('name', 'slug')
    paginator = Paginator(topics, items_per_page)
    current_page = paginator.get_page(page)

    return {
        'topics': list(current_page.object_list),
        'current_page': page,
        'num_pages': paginator.num_pages,
        'has_previous': current_page.has_previous(),
        'has_next': current_page.has_next(),
        'previous_page_number': (
            current_page.previous_page_number()
            if current_page.has_previous()
            else None
        ),
        'next_page_number': (
            current_page.next_page_number()
            if current_page.has_next()
            else None
        ),
    }


async def get_level3_menu(
    level1_choice: str,
    level2_choice: str,
    page: int = 1,
    items_per_page: int = ITEMS_PER_PAGE
):
    """Level 3 menu. Topics."""
    builder = InlineKeyboardBuilder()

    page_data = await get_level3_menu_data(
        level1_choice,
        level2_choice,
        page,
        items_per_page
    )
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
    builder.add(
        InlineKeyboardButton(
            text="👀 Показать все",
            callback_data=cb.Level3Callback(
                level1=level1_choice,
                level2=level2_choice,
                topic="all"
            ).pack()
        )
    )
    builder.adjust(NUMBER_OF_COLUMNS)

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
            callback_data='no_action'
        ))

        if page_data['has_next']:
            pagination_row.append(InlineKeyboardButton(
                text='▶️',
                callback_data=cb.PaginateLevel3Callback(
                    level1=level1_choice,
                    level2=level2_choice,
                    page=page_data['next_page_number']
                ).pack()
            ))
        builder.row(*pagination_row)

    builder.row(InlineKeyboardButton(
        text='⬅️ Назад',
        callback_data=cb.BackLevel2Callback(level1=level1_choice).pack()
    ))

    return builder.as_markup()


@sync_to_async
def get_content_menu_data(
    level1_choice: str,
    level2_choice: str,
    level3_choice: str,
    page: int = 1,
    items_per_page: int = ITEMS_PER_PAGE
):
    """Get a list of content."""
    filters = {
        'is_active': True,
        'paths__slug': level1_choice,
        'categories__slug': level2_choice
    }
    if level3_choice != "all":
        filters['topics__slug'] = level3_choice
    content_items = ContentFile.objects.filter(
        **filters
    ).distinct().values('name', 'id')
    paginator = Paginator(content_items, items_per_page)
    current_page = paginator.get_page(page)
    return {
        'content_items': list(current_page.object_list),
        'current_page': page,
        'num_pages': paginator.num_pages,
        'has_previous': current_page.has_previous(),
        'has_next': current_page.has_next(),
        'previous_page_number': (
            current_page.previous_page_number()
            if current_page.has_previous()
            else None
        ),
        'next_page_number': (
            current_page.next_page_number()
            if current_page.has_next()
            else None
        ),
    }


async def get_content_menu(
    level1_choice: str,
    level2_choice: str,
    level3_choice: str,
    page: int = 1,
    items_per_page: int = ITEMS_PER_PAGE
):
    """Content menu with a list of elements."""
    builder = InlineKeyboardBuilder()
    page_data = await get_content_menu_data(
        level1_choice,
        level2_choice,
        level3_choice,
        page,
        items_per_page
    )
    content_items = page_data['content_items']
    for item in content_items:
        builder.add(
            InlineKeyboardButton(
                text=item['name'],
                callback_data=cb.ContentDescriptionCallback(
                    level1=level1_choice,
                    level2=level2_choice,
                    level3=level3_choice,
                    content_item=item['id']
                ).pack()
            )
        )
    builder.adjust(1)

    if page_data['num_pages'] > 1:
        pagination_row = []
        if page_data['has_previous']:
            pagination_row.append(InlineKeyboardButton(
                text="◀️",
                callback_data=cb.PaginateContentCallback(
                    level1=level1_choice,
                    level2=level2_choice,
                    level3=level3_choice,
                    page=page_data['previous_page_number']
                ).pack()
            ))
        pagination_row.append(InlineKeyboardButton(
            text=f'{page_data["current_page"]}/{page_data["num_pages"]}',
            callback_data='no_action'
        ))
        if page_data['has_next']:
            pagination_row.append(InlineKeyboardButton(
                text="▶️",
                callback_data=cb.PaginateContentCallback(
                    level1=level1_choice,
                    level2=level2_choice,
                    level3=level3_choice,
                    page=page_data['next_page_number']
                ).pack()
            ))
        builder.row(*pagination_row)
    back_callback = (
        cb.BackLevel2Callback(level1=level1_choice)
        if level3_choice == "all"
        else cb.BackLevel3Callback(level1=level1_choice, level2=level2_choice)
    )
    builder.row(
        InlineKeyboardButton(
            text='⬅️ Назад',
            callback_data=back_callback.pack()
        )
    )

    return builder.as_markup()


@sync_to_async
def get_content_item_data(content_item_id: str) -> dict:
    """Get content item data by ID."""
    try:
        content_item = ContentFile.objects.get(
            id=content_item_id,
            is_active=True
        )

        return {
            'title': content_item.name,
            'description': getattr(
                content_item,
                'description',
                'Описание отсутствует'
            ),
            'content_type': content_item.file_type,
        }
    except ContentFile.DoesNotExist:
        return {
            'title': 'Материал не найден',
            'description': 'Извините, данный материал временно недоступен',
        }


@sync_to_async
def get_media_file_data(content_item_id: str) -> dict:
    """Get media file data."""
    try:
        content_item = ContentFile.objects.get(
            id=content_item_id,
            is_active=True
        )
        if not content_item.file:
            return {'error': 'Файл не найден'}
        return {
            'file_path': content_item.file.path,
            'file_name': content_item.file.name,
            'content_type': content_item.file_type,
            'file_obj': content_item.file
        }
    except ContentFile.DoesNotExist:
        return {'error': 'Материал не найден'}
    except Exception as e:
        return {'error': f'Ошибка: {str(e)}'}


@sync_to_async
def get_content_page_data(
    content_item_id: str,
    page: int,
    chars_per_page: int = 4000
) -> dict:
    """Get paginated data from a TXT content file."""
    try:
        content_item = ContentFile.objects.get(
            id=content_item_id,
            is_active=True
        )

        if not content_item.file or not content_item.file.name:
            return {
                'content': 'Файл не найден',
                'total_pages': 1,
                'current_page': 1
            }

        file_path = content_item.file.path

        if not os.path.exists(file_path):
            return {
                'content': 'Файл не найден на сервере',
                'total_pages': 1,
                'current_page': 1
            }

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content_text = f.read()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='cp1251') as f:
                content_text = f.read()
        total_chars = len(content_text)
        total_pages = (total_chars + chars_per_page - 1) // chars_per_page
        if total_pages == 0:
            return {
                'content': 'Файл пуст',
                'total_pages': 1,
                'current_page': 1
            }
        actual_page = min(max(1, page), total_pages)
        start_idx = (actual_page - 1) * chars_per_page
        end_idx = start_idx + chars_per_page
        page_content = content_text[start_idx:end_idx]
        return {
            'content': page_content,
            'total_pages': total_pages,
            'current_page': actual_page
        }
    except ContentFile.DoesNotExist:
        return {
            'content': "Материал не найден",
            'total_pages': 1,
            'current_page': 1
        }
    except Exception as e:
        print(f'Ошибка при чтении файла: {e}')
        return {
            'content': 'Ошибка при чтении файла',
            'total_pages': 1,
            'current_page': 1
        }


async def get_content_description(
    level1_choice: str,
    level2_choice: str,
    level3_choice: str,
    content_item: str
):
    """Get a page with content description, separating text and media."""
    content_data = await get_content_item_data(content_item)

    builder = InlineKeyboardBuilder()

    if content_data['content_type'] == 'TEXT':
        button_text = "📖 Читать"
        callback_data = cb.ContentReadCallback(
            level1=level1_choice,
            level2=level2_choice,
            level3=level3_choice,
            content_item=content_item,
            page=1
        )
    else:
        button_texts = {
            'IMAGE': '🖼️ Смотреть фото',
            'VIDEO': '🎥 Смотреть видео', 
            'PDF': '📄 Открыть документ',
            'AUDIO': '🎵 Слушать аудио'
        }
        button_text = button_texts.get(
            content_data['content_type'],
            '📁 Открыть')
        callback_data = cb.ContentMediaCallback(
            level1=level1_choice,
            level2=level2_choice,
            level3=level3_choice,
            content_item=content_item
        )

    builder.add(InlineKeyboardButton(
        text=button_text,
        callback_data=callback_data.pack()
    ))

    builder.add(InlineKeyboardButton(
        text='⬅️ Назад к списку',
        callback_data=cb.BackToContentListCallback(
            level1=level1_choice,
            level2=level2_choice,
            level3=level3_choice
        ).pack()
    ))

    builder.adjust(1)

    type_names = {
        'text': 'Текст',
        'photo': 'Фотография',
        'video': 'Видео',
        'document': 'Документ',
        'audio': 'Аудио'
    }

    description_text = (
        f'📚 <b>{content_data["title"]}</b>\n\n'
        f'{content_data["description"]}\n\n'
        f'📋 Тип: {type_names.get(content_data["content_type"], "Файл")}'
    )

    return description_text, builder.as_markup()


async def get_content_page(
    level1_choice: str,
    level2_choice: str,
    level3_choice: str,
    content_item: str,
    page: int = 1
):
    """Get a content page."""
    page_data = await get_content_page_data(content_item, page)
    builder = InlineKeyboardBuilder()
    if page_data['total_pages'] > 1:
        pagination_row = []
        if page > 1:
            pagination_row.append(InlineKeyboardButton(
                text='◀️ Предыдущая',
                callback_data=cb.ContentReadCallback(
                    level1=level1_choice,
                    level2=level2_choice,
                    level3=level3_choice,
                    content_item=content_item,
                    page=page-1
                ).pack()
            ))
        pagination_row.append(InlineKeyboardButton(
            text=f'{page}/{page_data["total_pages"]}',
            callback_data='no_action'
        ))
        if page < page_data['total_pages']:
            pagination_row.append(InlineKeyboardButton(
                text='Следующая ▶️',
                callback_data=cb.ContentReadCallback(
                    level1=level1_choice,
                    level2=level2_choice,
                    level3=level3_choice,
                    content_item=content_item,
                    page=page+1
                ).pack()
            ))

        builder.row(*pagination_row)
    builder.row(InlineKeyboardButton(
        text='⬅️ Назад к описанию',
        callback_data=cb.ContentDescriptionCallback(
            level1=level1_choice,
            level2=level2_choice,
            level3=level3_choice,
            content_item=content_item
        ).pack()
    ))
    content_text = (
        f'<b>Страница {page}</b>\n\n'
        f'{page_data['content']}'
    )

    return content_text, builder.as_markup()


async def get_media_back_keyboard(
    level1_choice: str,
    level2_choice: str,
    level3_choice: str,
    content_item: str
):
    """Get a Back button for media files."""
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text='⬅️ Назад к описанию',
        callback_data=cb.ContentDescriptionCallback(
            level1=level1_choice,
            level2=level2_choice,
            level3=level3_choice,
            content_item=content_item
        ).pack()
    ))
    return builder.as_markup()
