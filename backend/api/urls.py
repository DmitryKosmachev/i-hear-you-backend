from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenVerifyView

from api.views import (
    BotMessageViewSet,
    CategoryViewSet,
    ContentFileViewSet,
    PathViewSet,
    TopicViewSet,
    StatisticsAPIView,
    CookieTokenObtainPairView,
    CookieTokenRefreshView,
)


router = DefaultRouter()
router.register(r'path', PathViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'topics', TopicViewSet)
router.register(r'files', ContentFileViewSet)
router.register(r'botmessages', BotMessageViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/jwt/create/', CookieTokenObtainPairView.as_view(), name='jwt-create'),
    path('auth/jwt/refresh/', CookieTokenRefreshView.as_view(), name='jwt-refresh'),
    path('auth/jwt/verify/', TokenVerifyView.as_view(), name='jwt-verify'),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('statistics/', StatisticsAPIView.as_view(), name='statistics'),
    path(
        'docs/',
        SpectacularSwaggerView.as_view(url_name='schema'),
        name='swagger-ui'
    ),
]
