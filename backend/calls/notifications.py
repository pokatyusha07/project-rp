"""
Модуль отправки уведомлений пользователям через Telegram.
"""
import logging
from django.conf import settings
from aiogram import Bot
import asyncio

logger = logging.getLogger(__name__)


class TelegramNotifier:
    """
    Класс для отправки уведомлений через Telegram бота.
    """
    
    def __init__(self):
        """Инициализирует Telegram бота."""
        self.bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    
    def send_transcription_ready(self, user, call_id):
        """
        Отправляет уведомление о готовности транскрипции.
        
        Args:
            user: Объект пользователя
            call_id: ID звонка
        """
        if not user.telegram_id:
            logger.warning(f"Пользователь {user.username} не имеет Telegram ID")
            return
        
        message = (
            f"✅ <b>Транскрипция готова!</b>\n\n"
            f"🆔 ID звонка: <code>{call_id}</code>\n\n"
            f"Используйте /calls для просмотра результата."
        )
        
        asyncio.create_task(
            self._send_message(user.telegram_id, message)
        )
    
    def send_daily_report(self, admin, report):
        """
        Отправляет ежедневный отчет администратору.
        
        Args:
            admin: Объект администратора
            report: Объект DailyReport
        """
        if not admin.telegram_id:
            return
        
        message = (
            f"📊 <b>Ежедневный отчет за {report.date.strftime('%d.%m.%Y')}</b>\n\n"
            f"📞 Всего звонков: {report.total_calls}\n"
            f"✅ Завершено: {report.completed_calls}\n"
            f"❌ Ошибок: {report.failed_calls}\n"
            f"⏱ Общая длительность: {report.total_duration:.1f} сек\n"
            f"📈 Средняя длительность: {report.average_duration:.1f} сек"
        )
        
        asyncio.create_task(
            self._send_message(admin.telegram_id, message)
        )
    
    def send_error_notification(self, user, call_id, error):
        """
        Отправляет уведомление об ошибке обработки.
        
        Args:
            user: Объект пользователя
            call_id: ID звонка
            error: Текст ошибки
        """
        if not user.telegram_id:
            return
        
        message = (
            f"❌ <b>Ошибка обработки звонка</b>\n\n"
            f"🆔 ID звонка: <code>{call_id}</code>\n"
            f"⚠️ Ошибка: {error}\n\n"
            f"Попробуйте загрузить файл еще раз."
        )
        
        asyncio.create_task(
            self._send_message(user.telegram_id, message)
        )
    
    async def _send_message(self, chat_id, text):
        """
        Отправляет сообщение в Telegram.
        
        Args:
            chat_id: ID чата
            text: Текст сообщения
        """
        try:
            await self.bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode="HTML"
            )
            logger.info(f"Уведомление отправлено в чат {chat_id}")
        except Exception as e:
            logger.error(f"Ошибка отправки уведомления: {e}")
