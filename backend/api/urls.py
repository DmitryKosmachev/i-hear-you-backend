from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.views import (
    BotMessageViewSet,
    CategoryViewSet,
    ContentFileViewSet,
    TopicViewSet
)


router = DefaultRouter()
router.register(r'categories', CategoryViewSet)
router.register(r'topics', TopicViewSet)
router.register(r'files', ContentFileViewSet)
router.register(r'botmessages', BotMessageViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
