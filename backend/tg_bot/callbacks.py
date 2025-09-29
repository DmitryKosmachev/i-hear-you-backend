from typing import Optional

from aiogram.filters.callback_data import CallbackData


class BaseCallback(CallbackData, prefix='base'):
    level1: Optional[str] = None
    level2: Optional[str] = None
    level3: Optional[str] = None


class Level1Callback(BaseCallback, prefix='l1'):
    """Level 1 callback button."""

    choice: str


class Level2Callback(BaseCallback, prefix='l2'):
    """Level 2 callback button."""

    category: str


class Level3Callback(BaseCallback, prefix='l3'):
    """Level 3 callback button."""

    topic: str


class PaginateLevel2Callback(BaseCallback, prefix='pag2'):
    """Level 2 pagination."""

    page: int


class PaginateLevel3Callback(BaseCallback, prefix='pag3'):
    """Level 3 pagination."""

    page: int


class PaginateContentCallback(BaseCallback, prefix='pag_content'):
    """Content pagination."""

    page: int


class BackLevel1Callback(BaseCallback, prefix='back1'):
    """Return to Level 1."""


class BackLevel2Callback(BaseCallback, prefix='back2'):
    """Return to Level 2."""


class BackLevel3Callback(BaseCallback, prefix='back3'):
    """Return to Level 3."""


class ContentDescriptionCallback(CallbackData, prefix='content_desc'):
    """Content page with descriptions."""

    level1: str
    level2: str
    level3: str
    content_item: int


class ContentReadCallback(CallbackData, prefix='content_read'):
    """Content representation."""

    level1: str
    level2: str
    level3: str
    content_item: int
    page: int


class BackToContentListCallback(CallbackData, prefix='back_content_list'):
    """Back to the list of content."""

    level1: str
    level2: str
    level3: str


class ContentMediaCallback(CallbackData, prefix='content_media'):
    level1: str
    level2: str
    level3: str
    content_item: int
