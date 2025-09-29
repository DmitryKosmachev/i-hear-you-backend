from aiogram.filters.callback_data import CallbackData
from typing import Optional


class BaseCallback(CallbackData, prefix='base'):
    level1: Optional[str] = None
    level2: Optional[str] = None
    level3: Optional[str] = None


class Level1Callback(BaseCallback, prefix='l1'):
    """Выбор уровня 1"""
    choice: str


class Level2Callback(BaseCallback, prefix='l2'):
    """Выбор уровня 2"""
    category: str


class Level3Callback(BaseCallback, prefix='l3'):
    """Выбор уровня 3"""
    topic: str


class PaginateLevel2Callback(BaseCallback, prefix='pag2'):
    """Пагинация уровня 2"""
    page: int


class PaginateLevel3Callback(BaseCallback, prefix='pag3'):
    """Пагинация уровня 3"""
    page: int


class PaginateContentCallback(BaseCallback, prefix='pag_content'):
    """Пагинация контента"""
    page: int


class BackLevel1Callback(BaseCallback, prefix='back1'):
    """Назад на уровень 1"""


class BackLevel2Callback(BaseCallback, prefix='back2'):
    """Назад на уровень 2"""


class BackLevel3Callback(BaseCallback, prefix='back3'):
    """Назад на уровень 3"""


class ContentDescriptionCallback(CallbackData, prefix='content_desc'):
    """СТраница контента с описанием."""
    level1: str
    level2: str
    level3: str
    content_item: int


class ContentReadCallback(CallbackData, prefix='content_read'):
    """Представление контента."""
    level1: str
    level2: str
    level3: str
    content_item: int
    page: int


class BackToContentListCallback(CallbackData, prefix='back_content_list'):
    """Назад к списку контента."""
    level1: str
    level2: str
    level3: str


class ContentMediaCallback(CallbackData, prefix='content_media'):
    level1: str
    level2: str
    level3: str
    content_item: int
