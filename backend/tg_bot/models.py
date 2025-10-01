from django.db import models


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
