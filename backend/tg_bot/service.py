from asgiref.sync import sync_to_async
from content.models import Category


class CategoryService:
    @staticmethod
    @sync_to_async
    def get_all_categories():
        """Получить все активные категории"""
        return list(Category.objects.filter(is_active=True).values('name', 'slug'))
