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
    # Принимаем как строки (названия), так и объекты (с полем name или id)
    categories = serializers.ListField(
        child=serializers.JSONField(),
        required=False,
        allow_empty=True,
        write_only=True
    )
    topics = serializers.ListField(
        child=serializers.JSONField(),
        required=False,
        allow_empty=True,
        write_only=True
    )
    paths = serializers.ListField(
        child=serializers.JSONField(),
        required=False,
        allow_empty=True,
        write_only=True
    )

    rating = serializers.FloatField(read_only=True)
    rating_count = serializers.IntegerField(read_only=True)

    file = serializers.FileField(required=False, allow_null=True)
    external_url = serializers.URLField(required=False, allow_null=True)

    class Meta:
        model = ContentFile
        fields = [
            'id', 'name', 'file', 'external_url', 'description', 
            'file_type', 'is_active', 'created_at', 'rating', 'rating_count',
            'categories', 'topics', 'paths', 'file_size', 'file_size_human'
        ]

    def _convert_to_objects(self, data_list, model_class, field_name):
        """Преобразует список строк (названий) или объектов в список объектов модели."""
        import json
        
        if not data_list or data_list is None:
            return []
        
        # Если пришла JSON-строка - парсим её
        if isinstance(data_list, str):
            try:
                data_list = json.loads(data_list)
            except json.JSONDecodeError:
                # Если не JSON, считаем что это одно название
                data_list = [data_list]
        
        result = []
        for item in data_list:
            # Если это строка, которая выглядит как JSON - пробуем распарсить
            if isinstance(item, str):
                # Если строка начинается с [ или {, пробуем распарсить как JSON
                if item.strip().startswith(('[', '{')):
                    try:
                        parsed = json.loads(item)
                        # Если распарсили массив - обрабатываем элементы
                        if isinstance(parsed, list):
                            for parsed_item in parsed:
                                obj = self._get_object_from_item(parsed_item, model_class, field_name)
                                result.append(obj)
                            continue
                        # Если объект - обрабатываем его
                        elif isinstance(parsed, dict):
                            item = parsed
                        # Иначе используем как есть
                    except json.JSONDecodeError:
                        pass  # Используем строку как название
            
            obj = self._get_object_from_item(item, model_class, field_name)
            result.append(obj)
        
        return result
    
    def _get_object_from_item(self, item, model_class, field_name):
        """Получает объект модели из элемента (строка, число, словарь)."""
        # Если это словарь/объект - извлекаем name или id
        if isinstance(item, dict):
            search_value = item.get('name') or item.get('id')
            if not search_value:
                raise serializers.ValidationError(
                    {field_name: f'Объект должен содержать поле "name" или "id"'}
                )
        # Если это строка - используем её как название
        elif isinstance(item, str):
            search_value = item
        # Если это число - используем как ID
        elif isinstance(item, (int, float)):
            search_value = int(item)
        else:
            raise serializers.ValidationError(
                {field_name: f'Ожидалось название (строка), ID (число) или объект с полем "name"/"id", получен {type(item).__name__}'}
            )
        
        try:
            # Пробуем найти по ID (если search_value число или строка-число)
            if isinstance(search_value, int) or (isinstance(search_value, str) and search_value.isdigit()):
                obj = model_class.objects.get(pk=int(search_value))
            else:
                # Ищем по названию
                obj = model_class.objects.get(name=search_value)
            return obj
        except model_class.DoesNotExist:
            raise serializers.ValidationError(
                {field_name: f'{model_class.__name__} "{search_value}" не найден'}
            )
    

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
        
        # Возвращаем полные объекты категорий
        representation['categories'] = [
            {
                'id': cat.id,
                'name': cat.name,
                'slug': cat.slug,
                'is_active': cat.is_active,
                'created_at': cat.created_at.isoformat() if cat.created_at else None,
                'path': cat.path_id if hasattr(cat, 'path_id') else None
            }
            for cat in instance.categories.all()
        ]
        
        # Возвращаем полные объекты топиков
        representation['topics'] = [
            {
                'id': topic.id,
                'name': topic.name,
                'slug': topic.slug,
                'is_active': topic.is_active,
                'created_at': topic.created_at.isoformat() if topic.created_at else None
            }
            for topic in instance.topics.all()
        ]
        
        # Возвращаем полные объекты путей
        representation['paths'] = [
            {
                'id': path.id,
                'name': path.name,
                'slug': path.slug,
                'is_active': path.is_active,
                'created_at': path.created_at.isoformat() if path.created_at else None
            }
            for path in instance.paths.all()
        ]
        
        # Добавляем размер файла в байтах
        # Получаем размер файла напрямую из объекта модели
        if instance.file:
            try:
                # instance.file - это FileField объект, у которого есть атрибут size
                file_size = instance.file.size
                representation['file_size'] = file_size
                representation['file_size_human'] = self._format_file_size(file_size)
            except (OSError, ValueError, AttributeError):
                # Если файл не найден или ошибка доступа
                representation['file_size'] = None
                representation['file_size_human'] = None
        else:
            representation['file_size'] = None
            representation['file_size_human'] = None
        
        return representation
    
    def _format_file_size(self, size_bytes):
        """Форматирует размер файла в читаемый вид (KB, MB, GB)."""
        if size_bytes is None:
            return None
        
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"


class BotMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BotMessage
        fields = ['id', 'key', 'text', 'comment', 'updated_at']
        read_only_fields = ['id', 'key', 'updated_at']
