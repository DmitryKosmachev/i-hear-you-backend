from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CategoryViewSet, ContentFileViewSet, TopicViewSet


router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'topics', TopicViewSet)
router.register(r'files', ContentFileViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
