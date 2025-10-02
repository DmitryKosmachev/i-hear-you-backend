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


class PaginateLevel2Callback(BaseCallback, prefix='pl2'):
    """Level 2 pagination."""

    page: int


class PaginateLevel3Callback(BaseCallback, prefix='pl3'):
    """Level 3 pagination."""

    page: int


class PaginateContentCallback(BaseCallback, prefix='pc'):
    """Content pagination."""

    page: int


class BackLevel1Callback(BaseCallback, prefix='bl1'):
    """Return to Level 1."""


class BackLevel2Callback(BaseCallback, prefix='bl'):
    """Return to Level 2."""


class BackLevel3Callback(BaseCallback, prefix='bl3'):
    """Return to Level 3."""


class ContentDescriptionCallback(CallbackData, prefix='cdesc'):
    """Content page with descriptions."""

    level1: str
    level2: str
    level3: str
    content_item: int


class ContentReadCallback(CallbackData, prefix='cread'):
    """Content representation."""

    level1: str
    level2: str
    level3: str
    content_item: int
    page: int


class BackToContentListCallback(CallbackData, prefix='bcl'):
    """Back to the list of content."""

    level1: str
    level2: str
    level3: str


class ContentMediaCallback(CallbackData, prefix='cm'):
    level1: str
    level2: str
    level3: str
    content_item: int


class SearchCallback(CallbackData, prefix='search'):
    level1: str
    level2: str | None
    level3: str | None


class RateCallback(CallbackData, prefix="rate"):
    """Start rating for a content item."""
    content_id: int
    level1: str
    level2: str
    level3: str
    page: int = 1


class RateSubmitCallback(CallbackData, prefix="rsubmit"):
    """User selected a rating for a content item."""
    content_id: int
    rating: int
    level1: str
    level2: str
    level3: str
