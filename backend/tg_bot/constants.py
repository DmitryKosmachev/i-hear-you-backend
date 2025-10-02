PATH_COLUMNS = 1
MAX_CHARS_PER_COLUMN = 25
DEFAULT_COLUMNS = 2
ITEMS_PER_PAGE = 8
INACTIVE_DAYS_FOR_MESSAGE = 10
NOTIFICATION_PERIOD = 86400
NOTIFICATION_TIME = '12:00'
DEFAULT_REMINDER_MESSAGE = (
    'Мы по вам скучаем! Загляните к нам, у нас много нового 😊'
)
LEVEL_TEXTS = {
    'level1': (
        'Добро пожаловать! '
        'Пожалуйста, выберите, с каким запросом Вы к нам пришли:'
    ),
    'level2': 'Выберите категорию:',
    'level3': (
        'Категория:\n'
        '<b>{}</b>\n\n'
        'Выберите тему или нажмите "Показать все", '
        'чтобы показать все материалы:'
    )
}
CONTENT_HEADER = (
    'Категория: '
    '<b>{}</b>'
    '{}'
    '\n\nМатериалы:'
)
TOPIC_NAME_FORMAT = '\nТема: <b>{}</b>'
SHOW_ALL_BTN = '👀 Показать все'
BACK_BTN = '⬅️ Назад'
FILE_LOADING_MSG = '⏳ Файл загружается...'
PREVIOUS_PAGE_BTN = '◀️ Предыдущая'
NEXT_PAGE_BTN = 'Следующая ▶️'
TO_DESCRIPTION_BTN = '⬅️ Назад к описанию'
TO_LIST_BTN = '⬅️ Назад к списку'
SEARCH_BTN = '🔍 Поиск'
SEARCH_HINT_MSG = 'Введите запрос для поиска материала по названию:'
SEARCH_REPEAT_BTN = '🔍 Повторить поиск'
SEARCH_RESULTS_MSG = 'Результаты поиска для "{}":'
SEARCH_NOT_FOUND_MSG = 'Материалы не найдены. Попробуйте другой запрос.'
RATING_BTN = '⭐ Оценить материал'
RATING_REPLY_MSG = 'Спасибо за оценку!'
ERROR_MSG = 'Ошибка: {}'
