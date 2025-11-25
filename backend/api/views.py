from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response


from api.serializers import (
    BotMessageSerializer,
    CategorySerializer,
    ContentFileSerializer,
    PathSerializer,
    TopicSerializer
)
from content.models import Category, ContentFile, ContentRating, Topic, Path
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


class StatisticsAPIView(APIView):
    def get(self, request):
        stats = get_all_metrics()
        return Response(stats)
