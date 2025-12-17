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
    categories = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Category.objects.all(),
        required=False
    )
    topics = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Topic.objects.all(),
        required=False
    )
    paths = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Path.objects.all(),
        required=False
    )
    
    file = serializers.FileField(required=False, allow_null=True)
    external_url = serializers.URLField(required=False, allow_null=True)

    class Meta:
        model = ContentFile
        fields = '__all__'

    def validate(self, data):
        file_type = data.get('file_type')
        file = data.get('file')
        external_url = data.get('external_url')

        if file_type == ContentFile.FileType.LINK:
            if not external_url and not self.instance:
                raise serializers.ValidationError(
                    {'external_url': 'Для типа LINK необходимо указать URL'}
                )
            if external_url:
                data['file'] = None
        else:
            if not file and not self.instance:
                raise serializers.ValidationError(
                    {'file': 'Для файловых типов необходимо загрузить файл'}
                )
            if file:
                data['external_url'] = None
        return data

    def validate_file(self, value):
        if value and value.size > MAX_FILE_SIZE_MB * 1024 * 1024:
            raise serializers.ValidationError(
                f'File size exceeds the {MAX_FILE_SIZE_MB} MB limit.'
            )
        return value

    def create(self, validated_data):
        categories = validated_data.pop('categories', [])
        topics = validated_data.pop('topics', [])
        paths = validated_data.pop('paths', [])

        content_file = ContentFile.objects.create(**validated_data)

        if categories:
            content_file.categories.set(categories)
        if topics:
            content_file.topics.set(topics)
        if paths:
            content_file.paths.set(paths)

        return content_file

    def update(self, instance, validated_data):

        categories = validated_data.pop('categories', None)
        topics = validated_data.pop('topics', None)
        paths = validated_data.pop('paths', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if categories is not None:
            instance.categories.set(categories)
        if topics is not None:
            instance.topics.set(topics)
        if paths is not None:
            instance.paths.set(paths)

        return instance


class BotMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BotMessage
        fields = ['id', 'key', 'text', 'comment', 'updated_at']
        read_only_fields = ['id', 'key', 'updated_at']
