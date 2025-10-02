from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
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
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path(
        'docs/',
        SpectacularSwaggerView.as_view(url_name='schema'),
        name='swagger-ui'
    ),
]
