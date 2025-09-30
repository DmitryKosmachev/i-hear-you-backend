from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.text import slugify, Truncator

from content.constants import (
    MAX_DESCRIPTION_CHARS,
    MAX_FILENAME_CHARS,
    MAX_NAME_CHARS,
    MAX_OBJECT_CHARS,
    MAX_SLUG_CHARS,
    MAX_RATING_INT,
    MIN_RATING_INT,
    RATING_VALIDATION_ERROR
)
from users.models import BotUser


class Section(models.Model):
    """Abstract model for objects related to general struture."""

    name = models.CharField(
        'Name',
        max_length=MAX_NAME_CHARS,
        unique=True
    )
    slug = models.SlugField(
        'Slug',
        max_length=MAX_SLUG_CHARS,
        unique=True
    )
    is_active = models.BooleanField('Active', default=True)
    created_at = models.DateTimeField('Created', auto_now_add=True)

    class Meta:
        abstract = True
        ordering = ['name', 'slug']

    def __str__(self):
        return Truncator(self.name).chars(MAX_OBJECT_CHARS)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Path(Section):
    """Global path to content for different target audiences
    (parent, inquiring user etc.)
    """

    class Meta:
        verbose_name = 'content path'
        verbose_name_plural = 'Content paths'


class Category(Section):
    """Content category (articles, videos, books etc.)"""

    class Meta:
        verbose_name = 'category'
        verbose_name_plural = "Categories"


class Topic(Section):
    """Topic for content inside a category."""

    class Meta:
        verbose_name = 'topic'
        verbose_name_plural = "Topics"


class ContentFileQuerySet(models.query.QuerySet):
    def annotate_rating(self):
        """Annotate content queryset with user rating."""
        return self.annotate(rating=models.Avg('ratings__rating'))


class ContentFile(models.Model):
    """Content unit (file)."""

    class FileType(models.TextChoices):
        PDF = 'PDF', 'PDF document'
        IMAGE = 'IMAGE', 'Image'
        TEXT = 'TEXT', 'Text file'
        VIDEO = 'VIDEO', 'Video'
        AUDIO = 'AUDIO', 'Audio'
        OTHER = 'OTHER', 'Other file type'

    name = models.CharField('Filename', max_length=MAX_NAME_CHARS)
    file = models.FileField('File', upload_to='content/files/')
    description = models.TextField(
        'Description',
        max_length=MAX_DESCRIPTION_CHARS,
        blank=True
    )
    file_type = models.CharField(
        'File type',
        max_length=MAX_FILENAME_CHARS,
        choices=FileType.choices
    )
    paths = models.ManyToManyField(
        Path,
        blank=True,
        verbose_name='Content paths'
    )
    categories = models.ManyToManyField(Category, verbose_name='Categories')
    topics = models.ManyToManyField(Topic, verbose_name='Topics')
    is_active = models.BooleanField('Active', default=False)
    created_at = models.DateTimeField('Created', auto_now_add=True)
    objects = ContentFileQuerySet.as_manager()

    class Meta:
        default_related_name = 'files'
        verbose_name = 'file'
        verbose_name_plural = 'Files'
        ordering = ['name', 'file_type']

    def __str__(self):
        return Truncator(self.name).chars(MAX_OBJECT_CHARS)


class ContentRating(models.Model):
    """User rating for content."""

    content = models.ForeignKey(
        ContentFile,
        on_delete=models.CASCADE,
        verbose_name='Content unit'
    )
    user = models.ForeignKey(
        BotUser,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='User'
    )
    rating = models.PositiveSmallIntegerField(
        'Rating',
        validators=[
            MinValueValidator(MIN_RATING_INT, RATING_VALIDATION_ERROR),
            MaxValueValidator(MAX_RATING_INT, RATING_VALIDATION_ERROR)
        ]
    )
    created_at = models.DateTimeField('Created', auto_now_add=True)

    class Meta:
        default_related_name = 'ratings'
        ordering = ['created_at', 'content', 'rating', 'user']
        constraints = [
            models.UniqueConstraint(
                fields=['content', 'user'],
                name='unique_user_rating'
            )
        ]
        verbose_name = 'user rating'
        verbose_name_plural = 'Ratings'

    def __str__(self):
        return Truncator(f'{self.user}\'s rating').chars(MAX_OBJECT_CHARS)


class BotMessage(models.Model):
    """Bot messages."""
    key = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='message key'
    )
    text = models.TextField(verbose_name='message text')
    comment = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='comment'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Update time'
    )

    class Meta:
        verbose_name = 'bot message'
        verbose_name_plural = 'Bot messages'
        ordering = ['key']

    def __str__(self):
        return self.key
