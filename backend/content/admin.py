from django.contrib import admin
from .models import Category, ContentFile, ContentRating, Topic, Path


@admin.register(Path)
class PathAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("name",)


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "slug", "is_active", "created_at")
    list_filter = ("category", "is_active", "paths")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("category", "name")


@admin.register(ContentFile)
class ContentFileAdmin(admin.ModelAdmin):
    list_display = ("name", "file_type", "rating", "is_active", "created_at")
    list_filter = ("file_type", "is_active", "paths", "categories", "topics")
    search_fields = ("name",)
    filter_horizontal = ("paths",)
    ordering = ("name",)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate_rating()

    def rating(self, obj):
        return obj.rating


@admin.register(ContentRating)
class ContentRatingAdmin(admin.ModelAdmin):
    list_display = ['content', 'rating', 'user', 'created_at']
    list_filter = ['rating']
    search_fields = ['content', 'user']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('content', 'user')
