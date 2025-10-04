from datetime import timedelta

import asyncio
import schedule
from aiogram import Bot
from asgiref.sync import sync_to_async
from django.db.models import Count, Q
from django.utils import timezone

from content.models import ContentViewStat
from tg_stat_bot.constants import STATS_MESSAGE_TIME, TOP_CONTENT_NUMBER
from users.models import BotUser, StatBotUser


def get_new_users_last_week():
    last_week = timezone.now() - timedelta(days=7)
    new_users_count = BotUser.objects.filter(
        created_at__gte=last_week
    ).count()
    return new_users_count


def get_top_content_last_week(limit=TOP_CONTENT_NUMBER):
    last_week = timezone.now() - timedelta(days=7)
    top_content = ContentViewStat.objects.filter(
        viewed_at__gte=last_week
    ).values(
        'content_file__name',
        'content_file_id'
    ).annotate(
        view_count=Count('id')
    ).order_by('-view_count')[:limit]
    return top_content


def get_all_metrics():
    now = timezone.now()
    content_metrics = ContentViewStat.objects.aggregate(
        dau=Count(
            'user',
            filter=Q(viewed_at__gte=now - timedelta(days=1)),
            distinct=True
        ),
        wau=Count(
            'user',
            filter=Q(viewed_at__gte=now - timedelta(days=7)),
            distinct=True
        ),
        mau=Count(
            'user',
            filter=Q(viewed_at__gte=now - timedelta(days=30)),
            distinct=True
        ),
    )
    new_users = get_new_users_last_week()
    top_content = get_top_content_last_week()
    return {
        'dau': content_metrics['dau'],
        'wau': content_metrics['wau'],
        'mau': content_metrics['mau'],
        'new_users_last_week': new_users,
        'top_content_last_week': list(top_content)
    }


async def send_stats(bot: Bot):
    try:
        users = await sync_to_async(list)(StatBotUser.objects.all())
        metrics = await sync_to_async(get_all_metrics)()
        message_text = (
            '📊 Статистика активных пользователей:\n'
            f'👥 DAU (за сутки): {metrics["dau"]}\n'
            f'📈 WAU (за неделю): {metrics["wau"]}\n'
            f'🚀 MAU (за месяц): {metrics["mau"]}\n'
            f'🆕 Новые пользователи (неделя): '
            f'{metrics["new_users_last_week"]}\n\n'
        )
        if metrics['top_content_last_week']:
            message_text += "🔥 **Топ-5 контента за неделю:**\n"
            for i, item in enumerate(metrics['top_content_last_week'], 1):
                content_title = item.get('content_file__name')
                message_text += (
                    f'{i}. {content_title} - '
                    f'{item["view_count"]} просмотров\n'
                )
        else:
            message_text += '📭 За неделю нет данных о просмотрах контента'

        for user in users:
            try:
                await bot.send_message(
                    chat_id=user.telegram_id,
                    text=message_text,
                )
                await asyncio.sleep(0.1)
            except Exception as e:
                print(f'Ошибка отправки {user.telegram_id}: {e}')

    except Exception as e:
        print(f'Общая ошибка в send_stats: {e}')


async def send_start_stats():
    try:
        metrics = await sync_to_async(get_all_metrics)()
        message_text = (
            '📊 Статистика активных пользователей:\n'
            f'👥 DAU (за сутки): {metrics["dau"]}\n'
            f'📈 WAU (за неделю): {metrics["wau"]}\n'
            f'🚀 MAU (за месяц): {metrics["mau"]}\n'
            f'🆕 Новые пользователи (неделя): '
            f'{metrics["new_users_last_week"]}\n\n'
        )
        if metrics['top_content_last_week']:
            message_text += "🔥 **Топ-5 контента за неделю:**\n"
            for i, item in enumerate(metrics['top_content_last_week'], 1):
                content_title = item.get('content_file__name')
                message_text += (
                    f'{i}. {content_title} - '
                    f'{item["view_count"]} просмотров\n'
                )
        else:
            message_text += '📭 За неделю нет данных о просмотрах контента'
    except Exception as e:
        message_text = (f'Общая ошибка отправки статистики: {e}')
    return message_text


def run_async_job(bot):
    asyncio.create_task(send_stats(bot))


async def start_scheduler(bot: Bot):
    schedule.every().monday.at(STATS_MESSAGE_TIME).do(run_async_job, bot)
    while True:
        schedule.run_pending()
        await asyncio.sleep(60)
