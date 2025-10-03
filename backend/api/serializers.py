from django.contrib.auth import get_user_model
from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from content.constants import MAX_FILE_SIZE_MB
from content.models import Category, ContentFile, Path, Topic
from tg_bot.models import BotMessage


User = get_user_model()


class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        model = User
        fields = [
            'email',
            'id',
            'first_name',
            'last_name',
            'password',
        ]

    def create(self, validated_data):
        return super().create(validated_data)


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'email',
            'id',
            'first_name',
            'last_name',
        ]


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['email'] = user.email
        token['full_name'] = user.get_full_name()
        return token


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class TopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Topic
        fields = '__all__'


class PathSerializer(serializers.ModelSerializer):
    class Meta:
        model = Path
        fields = '__all__'


class ContentFileSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, required=False)
    topics = TopicSerializer(many=True, required=False)
    paths = PathSerializer(many=True, required=False)
    file = serializers.FileField(required=True)

    class Meta:
        model = ContentFile
        fields = '__all__'

    def validate_file(self, value):
        if value.size > MAX_FILE_SIZE_MB * 1024 * 1024:
            raise serializers.ValidationError(
                f'File size exceeds the {MAX_FILE_SIZE_MB} MB limit.'
            )
        return value


class BotMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BotMessage
        fields = ['id', 'key', 'text', 'comment', 'updated_at']
        read_only_fields = ['id', 'key', 'updated_at']
