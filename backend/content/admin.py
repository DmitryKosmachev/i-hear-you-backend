from django.contrib import admin

from content.models import (
    Category,
    ContentFile,
    ContentRating,
    ContentViewStat,
    Topic,
    Path
)


@admin.register(Path)
class PathAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ['name']}
    search_fields = ['name']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ['name']}
    ordering = ['name']


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ['name']}
    ordering = ['name']


@admin.register(ContentFile)
class ContentFileAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'file_type',
        'rating',
        'rating_count',
        'get_paths',
        'get_topics',
        'get_categories',
        'is_active',
        'created_at'
    ]
    list_filter = ['is_active', 'file_type', 'paths', 'categories', 'topics']
    list_editable = ['is_active']
    search_fields = ['name']
    filter_horizontal = ['categories', 'paths', 'topics']
    ordering = ['name']

    def get_queryset(self, request):
        return super(
        ).get_queryset(
            request
        ).annotate_rating().prefetch_related('categories', 'topics')

    def rating(self, obj):
        return obj.rating

    @admin.display(description='Users rated')
    def rating_count(self, obj):
        return obj.rating_count

    @admin.display(description='Paths')
    def get_paths(self, obj):
        return ", ".join(path.name for path in obj.paths.all())

    @admin.display(description='Topics')
    def get_topics(self, obj):
        return ", ".join(topic.name for topic in obj.topics.all())

    @admin.display(description='Categories')
    def get_categories(self, obj):
        return ", ".join(category.name for category in obj.categories.all())


@admin.register(ContentRating)
class ContentRatingAdmin(admin.ModelAdmin):
    list_display = ['content', 'rating', 'user', 'created_at']
    list_filter = ['rating']
    search_fields = ['content', 'user']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('content', 'user')


@admin.register(ContentViewStat)
class ContentViewStatAdmin(admin.ModelAdmin):
    list_display = ['user', 'content_file', 'viewed_at']
    search_fields = ['user', 'content_file', 'viewed_at']
