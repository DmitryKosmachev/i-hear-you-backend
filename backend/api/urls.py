from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ThemeViewSet, ContentFileViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'themes', ThemeViewSet)
router.register(r'files', ContentFileViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
