from rest_framework import viewsets
from rest_framework_simplejwt.views import TokenObtainPairView

from api.serializers import (
    BotMessageSerializer,
    CategorySerializer,
    ContentFileSerializer,
    CustomTokenObtainPairSerializer,
    TopicSerializer,
    PathSerializer
)
from content.models import BotMessage, Category, ContentFile, Topic, Path


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


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
