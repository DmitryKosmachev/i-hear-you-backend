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
    categories = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True,
        write_only=True
    )
    topics = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True,
        write_only=True
    )
    paths = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_empty=True,
        write_only=True
    )
    
    def _convert_to_objects(self, data_list, model_class, field_name):
        if not data_list or data_list is None:
            return []
        
        result = []
        for item in data_list:
            if not isinstance(item, str):
                raise serializers.ValidationError(
                    {field_name: f'Ожидалось название (строка), получен {type(item).__name__}'}
                )
            
            try:
                obj = model_class.objects.get(name=item)
                result.append(obj)
            except model_class.DoesNotExist:
                raise serializers.ValidationError(
                    {field_name: f'{model_class.__name__} "{item}" не найден'}
                )
        return result
    
    file = serializers.FileField(required=False, allow_null=True)
    external_url = serializers.URLField(required=False, allow_null=True)

    class Meta:
        model = ContentFile
        fields = [
            'id', 'name', 'file', 'external_url', 'description', 
            'file_type', 'is_active', 'created_at', 'rating', 'rating_count',
            'categories', 'topics', 'paths'
        ]

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
        categories_data = validated_data.pop('categories', [])
        topics_data = validated_data.pop('topics', [])
        paths_data = validated_data.pop('paths', [])
        
        categories = self._convert_to_objects(categories_data, Category, 'categories')
        topics = self._convert_to_objects(topics_data, Topic, 'topics')
        paths = self._convert_to_objects(paths_data, Path, 'paths')

        content_file = ContentFile.objects.create(**validated_data)

        if categories:
            content_file.categories.set(categories)
        if topics:
            content_file.topics.set(topics)
        if paths:
            content_file.paths.set(paths)

        return content_file

    def update(self, instance, validated_data):
        categories_data = validated_data.pop('categories', None)
        topics_data = validated_data.pop('topics', None)
        paths_data = validated_data.pop('paths', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if categories_data is not None:
            categories = self._convert_to_objects(categories_data, Category, 'categories')
            instance.categories.set(categories)
        if topics_data is not None:
            topics = self._convert_to_objects(topics_data, Topic, 'topics')
            instance.topics.set(topics)
        if paths_data is not None:
            paths = self._convert_to_objects(paths_data, Path, 'paths')
            instance.paths.set(paths)

        return instance
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['categories'] = [cat.name for cat in instance.categories.all()]
        representation['topics'] = [topic.name for topic in instance.topics.all()]
        representation['paths'] = [path.name for path in instance.paths.all()]
        return representation


class BotMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BotMessage
        fields = ['id', 'key', 'text', 'comment', 'updated_at']
        read_only_fields = ['id', 'key', 'updated_at']
