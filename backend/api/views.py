from django.db.migrations.serializer import TypeSerializer
from rest_framework import viewsets
from rest_framework_simplejwt.views import TokenObtainPairView
from content.models import Category, Theme, ContentFile, Type
from .serializers import CategorySerializer, ThemeSerializer, ContentFileSerializer, CustomTokenObtainPairSerializer, TypeSerializer



class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ThemeViewSet(viewsets.ModelViewSet):
    queryset = Theme.objects.all()
    serializer_class = ThemeSerializer


class ContentFileViewSet(viewsets.ModelViewSet):
    queryset = ContentFile.objects.all()
    serializer_class = ContentFileSerializer


class TypeViewSet(viewsets.ModelViewSet):
    queryset = Type.objects.all()
    serializer_class = TypeSerializer

