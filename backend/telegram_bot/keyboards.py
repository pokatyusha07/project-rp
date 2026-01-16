"""
Клавиатуры для Telegram бота.
"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


def get_main_keyboard():
    """
    Возвращает главную клавиатуру бота.
    """
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📞 Мои звонки"),
                KeyboardButton(text="📊 Статистика")
            ],
            [
                KeyboardButton(text="🔍 Поиск"),
                KeyboardButton(text="⚙️ Настройки")
            ],
            [
                KeyboardButton(text="❓ Помощь")
            ]
        ],
        resize_keyboard=True
    )
    return keyboard


def get_calls_keyboard(calls):
    """
    Возвращает клавиатуру со списком звонков.
    """
    buttons = []
    
    for call in calls[:5]:  # Показываем до 5 звонков
        buttons.append([
            InlineKeyboardButton(
                text=f"🆔 {str(call.id)[:8]}... - {call.get_status_display()}",
                callback_data=f"call_{call.id}"
            )
        ])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def get_call_detail_keyboard(call_id):
    """
    Возвращает клавиатуру для детального просмотра звонка.
    """
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📝 Транскрипция",
                    callback_data=f"transcription_{call_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📊 Анализ",
                    callback_data=f"analysis_{call_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔙 Назад к списку",
                    callback_data="back_to_calls"
                )
            ]
        ]
    )
    return keyboard


def get_settings_keyboard(notifications_enabled):
    """
    Возвращает клавиатуру настроек.
    """
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔔 Выключить уведомления" if notifications_enabled else "🔔 Включить уведомления",
                    callback_data="toggle_notifications"
                )
            ]
        ]
    )
    return keyboard


def get_category_keyboard():
    """
    Возвращает клавиатуру с категориями для фильтрации.
    """
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📞 Все", callback_data="filter_all"),
                InlineKeyboardButton(text="😠 Жалобы", callback_data="filter_complaint")
            ],
            [
                InlineKeyboardButton(text="🛒 Заказы", callback_data="filter_order"),
                InlineKeyboardButton(text="💬 Поддержка", callback_data="filter_support")
            ]
        ]
    )
    return keyboard
