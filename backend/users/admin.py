from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from users.models import BotUser, StaffUser


@admin.register(StaffUser)
class StaffUserAdmin(UserAdmin):
    list_display = [
        'email',
        'first_name',
        'last_name',
        'is_staff',
        'is_superuser'
    ]
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['first_name']

    fieldsets = [
        [
            'Персональная информация',
            {'fields': ['first_name', 'last_name', 'email']}
        ],
        [
            'Права доступа',
            {'fields': ['is_active', 'is_staff', 'is_superuser']}
        ]
    ]

    add_fieldsets = [
        [
            None,
            {
                'classes': ['wide'],
                'fields': [
                    'email',
                    'first_name',
                    'last_name',
                    'password1',
                    'password2'
                ]
            }
        ]
    ]


@admin.register(BotUser)
class BotUserAdmin(admin.ModelAdmin):
    list_display = ['telegram_id']
