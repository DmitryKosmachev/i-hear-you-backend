from datetime import timedelta
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from django.conf import settings

from api.serializers import (
    BotMessageSerializer,
    CategorySerializer,
    ContentFileSerializer,
    PathSerializer,
    TopicSerializer,
    CustomTokenObtainPairSerializer,
)
from content.models import Category, ContentFile, Topic, Path
from tg_bot.models import BotMessage
from tg_stat_bot.utils import get_all_metrics


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class TopicViewSet(viewsets.ModelViewSet):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer


class ContentFileViewSet(viewsets.ModelViewSet):
    queryset = ContentFile.objects.annotate_rating()
    serializer_class = ContentFileSerializer


class PathViewSet(viewsets.ModelViewSet):
    queryset = Path.objects.all()
    serializer_class = PathSerializer


class BotMessageViewSet(viewsets.ModelViewSet):
    queryset = BotMessage.objects.all()
    serializer_class = BotMessageSerializer
    http_method_names = ['get', 'put', 'patch', 'head', 'options']
    lookup_field = 'key'


class StatisticsAPIView(APIView):
    def get(self, request):
        stats = get_all_metrics()
        return Response(stats)


class CookieTokenObtainPairView(TokenObtainPairView):
    """
    Кастомный view для создания токенов.
    Возвращает access token в ответе, refresh token сохраняет в httpOnly cookie.
    """
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        access_token = serializer.validated_data.get('access')
        refresh_token = serializer.validated_data.get('refresh')

        response = Response(
            {'access': str(access_token)},
            status=status.HTTP_200_OK
        )

        refresh_token_lifetime = settings.SIMPLE_JWT.get('REFRESH_TOKEN_LIFETIME', timedelta(days=7))
        max_age = int(refresh_token_lifetime.total_seconds())

        response.set_cookie(
            key='refresh_token',
            value=str(refresh_token),
            max_age=max_age,
            httponly=True,
            secure=not settings.DEBUG,
            samesite='Lax',
            path='/',
        )

        return response


class CookieTokenRefreshView(TokenRefreshView):
    """
    Кастомный view для обновления токенов.
    Читает refresh token из httpOnly cookie вместо body запроса.
    """

    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh_token')

        if not refresh_token:
            return Response(
                {'detail': 'Refresh token not found in cookie'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        data = {'refresh': refresh_token}
        
        serializer = self.get_serializer(data=data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        access_token = serializer.validated_data.get('access')
        
        return Response(
            {'access': str(access_token)},
            status=status.HTTP_200_OK
        )
