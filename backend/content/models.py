from django.db import models
from django.utils.text import slugify
import os


class Type(models.Model):
    """Тип контента."""
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name="Название типа"
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        verbose_name="URL-идентификатор",
        blank=True
    )

    class Meta:
        verbose_name = "Тип контента"
        verbose_name_plural = "Типы контента"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Category(models.Model):
    """Модель категории контента."""
    name = models.CharField(max_length=100, unique=True, verbose_name="Название категории")
    slug = models.SlugField(max_length=100, unique=True, blank=True, verbose_name="URL-идентификатор")
    types = models.ManyToManyField(
        "Type",
        related_name="categories",
        blank=True,
        verbose_name="Типы контента"
    )
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

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
    """Модель темы внутри категории."""
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='themes', verbose_name="Категория")
    name = models.CharField(max_length=200, verbose_name="Название темы")
    slug = models.SlugField(max_length=200, blank=True, verbose_name="URL-идентификатор")
    types = models.ManyToManyField(
        "Type",
        related_name="themes",
        blank=True,
        verbose_name="Типы контента"
    )
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

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
    """Модель файла для темы."""

    class FileType(models.TextChoices):
        PDF = "PDF", "PDF документ"
        IMAGE = "IMAGE", "Изображение"
        TEXT = "TEXT", "Текстовый файл"
        VIDEO = "VIDEO", "Видео"
        AUDIO = "AUDIO", "Аудио"
        OTHER = "OTHER", "Другой файл"

    name = models.CharField(max_length=200, verbose_name="Название файла")
    file = models.FileField(upload_to='content/files/', verbose_name="Файл")
    file_type = models.CharField(
        max_length=10,
        choices=FileType.choices,
        verbose_name="Тип файла",
        blank=False,
        null=False
    )
    types = models.ManyToManyField(
        "Type",
        related_name="files",
        blank=True,
        verbose_name="Типы контента"
    )
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Файл"
        verbose_name_plural = "Файлы"
        ordering = ['name']

    def __str__(self):
        return f"{self.name}"
