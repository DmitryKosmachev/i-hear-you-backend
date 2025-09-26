from django.db import models
from django.utils.text import slugify
import os


class Category(models.Model):
    """Модель категории контента"""
    name = models.CharField(
        max_length=100,
        verbose_name="Название категории",
        unique=True
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        verbose_name="URL-идентификатор",
        blank=True
    )
    for_adults = models.BooleanField(
        default=False,
        verbose_name="Для взрослых"
    )
    for_children = models.BooleanField(
        default=False,
        verbose_name="Для детей"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активна"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Theme(models.Model):
    """Модель темы внутри категории"""
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='themes',
        verbose_name="Категория"
    )
    name = models.CharField(
        max_length=200,
        verbose_name="Название темы"
    )
    slug = models.SlugField(
        max_length=200,
        verbose_name="URL-идентификатор",
        blank=True
    )
    for_adults = models.BooleanField(
        default=False,
        verbose_name="Для взрослых"
    )
    for_children = models.BooleanField(
        default=False,
        verbose_name="Для детей"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активна"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )

    class Meta:
        verbose_name = "Тема"
        verbose_name_plural = "Темы"
        ordering = ['category', 'name']
        unique_together = ['category', 'slug']

    def __str__(self):
        return f"{self.category.name} - {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class ContentFile(models.Model):
    """Модель файла для темы"""

    class FileType(models.TextChoices):
        PDF = 'PDF', 'PDF документ'
        IMAGE = 'IMAGE', 'Изображение'
        TEXT = 'TEXT', 'Текстовый файл'
        VIDEO = 'VIDEO', 'Видео'
        AUDIO = 'AUDIO', 'Аудио'
        OTHER = 'OTHER', 'Другой файл'

    theme = models.ForeignKey(
        Theme,
        on_delete=models.CASCADE,
        related_name='files',
        verbose_name="Тема"
    )
    name = models.CharField(
        max_length=200,
        verbose_name="Название файла"
    )
    file = models.FileField(
        upload_to='content/files/%Y/%m/%d/',
        verbose_name="Файл"
    )
    file_type = models.CharField(
        max_length=10,
        choices=FileType.choices,
        verbose_name="Тип файла"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активен"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )

    class Meta:
        verbose_name = "Файл"
        verbose_name_plural = "Файлы"
        ordering = ['theme', 'name']

    def __str__(self):
        return f"{self.name} ({self.get_file_type_display()})"

    def save(self, *args, **kwargs):
        # Автоматически определяем тип файла при сохранении
        if not self.file_type:
            self.file_type = self._detect_file_type()
        super().save(*args, **kwargs)

    def _detect_file_type(self):
        """Автоматическое определение типа файла по расширению"""
        if not self.file:
            return self.FileType.OTHER

        filename = self.file.name.lower()
        extension = os.path.splitext(filename)[1]

        file_type_mapping = {
            '.pdf': self.FileType.PDF,
            '.jpg': self.FileType.IMAGE, '.jpeg': self.FileType.IMAGE,
            '.png': self.FileType.IMAGE, '.gif': self.FileType.IMAGE,
            '.bmp': self.FileType.IMAGE, '.webp': self.FileType.IMAGE,
            '.txt': self.FileType.TEXT, '.doc': self.FileType.TEXT,
            '.docx': self.FileType.TEXT,
            '.mp4': self.FileType.VIDEO, '.avi': self.FileType.VIDEO,
            '.mov': self.FileType.VIDEO, '.mkv': self.FileType.VIDEO,
            '.mp3': self.FileType.AUDIO, '.wav': self.FileType.AUDIO,
            '.ogg': self.FileType.AUDIO,
        }

        return file_type_mapping.get(extension, self.FileType.OTHER)