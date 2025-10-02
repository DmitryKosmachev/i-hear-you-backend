from django.contrib import admin

from tg_bot.models import BotMessage


@admin.register(BotMessage)
class BotMessageAdmin(admin.ModelAdmin):
    list_display = ['key', 'text', 'updated_at']
    search_fields = ['key', 'text', 'comment']
