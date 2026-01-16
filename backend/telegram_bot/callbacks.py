"""
Обработчики callback запросов от inline кнопок.
"""
import logging
from aiogram import Dispatcher, types, F
from aiogram.fsm.context import FSMContext
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async

from .keyboards import get_settings_keyboard
from .utils import format_call_info

User = get_user_model()
logger = logging.getLogger(__name__)


def register_callbacks(dp: Dispatcher):
    """
    Регистрирует все callback обработчики.
    """
    dp.callback_query.register(call_detail_callback, F.data.startswith('call_'))
    dp.callback_query.register(transcription_callback, F.data.startswith('transcription_'))
    dp.callback_query.register(analysis_callback, F.data.startswith('analysis_'))
    dp.callback_query.register(back_to_calls_callback, F.data == 'back_to_calls')
    dp.callback_query.register(toggle_notifications_callback, F.data == 'toggle_notifications')


async def call_detail_callback(callback: types.CallbackQuery):
    """
    Обработчик для просмотра деталей звонка.
    """
    call_id = callback.data.replace('call_', '')
    telegram_id = callback.from_user.id
    
    # Получаем пользователя
    user = await sync_to_async(User.objects.filter(telegram_id=telegram_id).first)()
    
    if not user:
        await callback.answer("❌ Вы не зарегистрированы")
        return
    
    # Получаем звонок
    from calls.models import Call
    
    call = await sync_to_async(
        lambda: Call.objects.filter(id=call_id, user=user)
        .select_related('transcription', 'analysis')
        .first()
    )()
    
    if not call:
        await callback.answer("❌ Звонок не найден")
        return
    
    # Формируем информацию
    from .keyboards import get_call_detail_keyboard
    info_text = format_call_info(call)
    
    await callback.message.edit_text(
        info_text,
        parse_mode="HTML",
        reply_markup=get_call_detail_keyboard(call_id)
    )
    
    await callback.answer()


async def transcription_callback(callback: types.CallbackQuery):
    """
    Обработчик для просмотра транскрипции.
    """
    call_id = callback.data.replace('transcription_', '')
    telegram_id = callback.from_user.id
    
    # Получаем пользователя
    user = await sync_to_async(User.objects.filter(telegram_id=telegram_id).first)()
    
    if not user:
        await callback.answer("❌ Вы не зарегистрированы")
        return
    
    # Получаем звонок с транскрипцией
    from calls.models import Call
    
    call = await sync_to_async(
        lambda: Call.objects.filter(id=call_id, user=user)
        .select_related('transcription')
        .first()
    )()
    
    if not call:
        await callback.answer("❌ Звонок не найден")
        return
    
    if not hasattr(call, 'transcription'):
        await callback.answer("❌ Транскрипция еще не готова")
        return
    
    transcription = call.transcription
    
    # Формируем текст (ограничиваем длину)
    text = transcription.text
    if len(text) > 3000:
        text = text[:3000] + "...\n\n(текст сокращен)"
    
    transcription_text = f"""
📝 <b>Транскрипция звонка</b>

🆔 ID: <code>{call.id}</code>
🎯 Уверенность: {transcription.confidence:.1f}%

<b>Текст:</b>
{text}
"""
    
    await callback.message.edit_text(
        transcription_text,
        parse_mode="HTML",
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.InlineKeyboardButton(
                        text="🔙 Назад",
                        callback_data=f"call_{call_id}"
                    )
                ]
            ]
        )
    )
    
    await callback.answer()


async def analysis_callback(callback: types.CallbackQuery):
    """
    Обработчик для просмотра анализа звонка.
    """
    call_id = callback.data.replace('analysis_', '')
    telegram_id = callback.from_user.id
    
    # Получаем пользователя
    user = await sync_to_async(User.objects.filter(telegram_id=telegram_id).first)()
    
    if not user:
        await callback.answer("❌ Вы не зарегистрированы")
        return
    
    # Получаем звонок с анализом
    from calls.models import Call
    
    call = await sync_to_async(
        lambda: Call.objects.filter(id=call_id, user=user)
        .select_related('analysis')
        .first()
    )()
    
    if not call:
        await callback.answer("❌ Звонок не найден")
        return
    
    if not hasattr(call, 'analysis'):
        await callback.answer("❌ Анализ еще не готов")
        return
    
    analysis = call.analysis
    
    # Формируем текст анализа
    keywords_text = ", ".join(analysis.keywords[:10]) if analysis.keywords else "Нет"
    
    sentiment_emoji = {
        'positive': '😊',
        'neutral': '😐',
        'negative': '😞'
    }.get(analysis.sentiment, '❓')
    
    analysis_text = f"""
📊 <b>Анализ звонка</b>

🆔 ID: <code>{call.id}</code>
📁 Категория: {analysis.get_category_display() if analysis.category else 'Не определена'}
{sentiment_emoji} Тональность: {analysis.sentiment or 'Не определена'}

🔑 <b>Ключевые слова:</b>
{keywords_text}

📝 <b>Краткое содержание:</b>
{analysis.summary or 'Не доступно'}
"""
    
    await callback.message.edit_text(
        analysis_text,
        parse_mode="HTML",
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    types.InlineKeyboardButton(
                        text="🔙 Назад",
                        callback_data=f"call_{call_id}"
                    )
                ]
            ]
        )
    )
    
    await callback.answer()


async def back_to_calls_callback(callback: types.CallbackQuery):
    """
    Обработчик для возврата к списку звонков.
    """
    from .handlers import my_calls_handler
    await my_calls_handler(callback.message)
    await callback.answer()


async def toggle_notifications_callback(callback: types.CallbackQuery):
    """
    Обработчик для переключения уведомлений.
    """
    telegram_id = callback.from_user.id
    
    # Получаем пользователя
    user = await sync_to_async(User.objects.filter(telegram_id=telegram_id).first)()
    
    if not user:
        await callback.answer("❌ Вы не зарегистрированы")
        return
    
    # Переключаем уведомления
    user.notifications_enabled = not user.notifications_enabled
    await sync_to_async(user.save)()
    
    settings_text = f"""
⚙️ <b>Настройки</b>

🔔 Уведомления: {'✅ Включены' if user.notifications_enabled else '❌ Выключены'}
"""
    
    await callback.message.edit_text(
        settings_text,
        parse_mode="HTML",
        reply_markup=get_settings_keyboard(user.notifications_enabled)
    )
    
    await callback.answer(
        f"✅ Уведомления {'включены' if user.notifications_enabled else 'выключены'}"
    )
