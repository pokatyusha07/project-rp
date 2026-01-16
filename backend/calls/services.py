"""
Сервисы для транскрипции и анализа звонков.
"""
import whisper
import torch
from pydub import AudioSegment
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import tempfile
import os
import logging
from collections import Counter
import re

logger = logging.getLogger(__name__)


class TranscriptionService:
    """
    Сервис для транскрипции аудио файлов с использованием Whisper.
    Поддерживает отправку промежуточных результатов через WebSocket.
    """
    
    def __init__(self):
        """Инициализирует модель Whisper."""
        from django.conf import settings
        
        model_name = settings.WHISPER_MODEL
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        logger.info(f"Загрузка модели Whisper: {model_name} на {device}")
        self.model = whisper.load_model(model_name, device=device)
        self.channel_layer = get_channel_layer()
    
    def transcribe(self, call):
        """
        Транскрибирует аудио файл звонка.
        
        Args:
            call: Объект Call для транскрипции
            
        Returns:
            dict: Данные транскрипции
        """
        from .models import Transcription
        
        logger.info(f"Начало транскрипции звонка {call.id}")
        
        try:
            # Получаем путь к аудио файлу
            audio_path = call.audio_file.path
            
            # Конвертируем аудио в WAV если нужно
            audio_path = self._prepare_audio(audio_path)
            
            # Получаем длительность аудио
            audio = AudioSegment.from_file(audio_path)
            duration = len(audio) / 1000.0  # в секундах
            call.duration = duration
            call.save()
            
            # Отправляем начальное уведомление
            self._send_progress(call.id, 0, "Начало транскрипции...")
            
            # Транскрибируем с промежуточными результатами
            result = self.model.transcribe(
                audio_path,
                language=call.language,
                verbose=True,
                task='transcribe'
            )
            
            # Обрабатываем сегменты
            segments = []
            full_text = []
            
            for i, segment in enumerate(result['segments']):
                segment_data = {
                    'start': segment['start'],
                    'end': segment['end'],
                    'text': segment['text'].strip(),
                    'confidence': segment.get('confidence', 0)
                }
                segments.append(segment_data)
                full_text.append(segment['text'].strip())
                
                # Отправляем прогресс по сегментам
                progress = int((i + 1) / len(result['segments']) * 100)
                self._send_progress(
                    call.id,
                    progress,
                    segment['text'].strip(),
                    segment_data
                )
            
            # Создаем транскрипцию
            transcription_text = ' '.join(full_text)
            avg_confidence = sum(s.get('confidence', 0) for s in segments) / len(segments) if segments else 0
            
            transcription = Transcription.objects.create(
                call=call,
                text=transcription_text,
                confidence=avg_confidence * 100,
                segments=segments
            )
            
            logger.info(f"Транскрипция звонка {call.id} завершена")
            
            return {
                'text': transcription_text,
                'segments': segments,
                'confidence': avg_confidence
            }
            
        except Exception as e:
            logger.error(f"Ошибка транскрипции звонка {call.id}: {str(e)}")
            self._send_error(call.id, str(e))
            raise
    
    def _prepare_audio(self, audio_path):
        """
        Подготавливает аудио файл для транскрипции.
        Конвертирует в WAV если необходимо.
        """
        # Если файл уже WAV, возвращаем как есть
        if audio_path.lower().endswith('.wav'):
            return audio_path
        
        # Конвертируем в WAV
        audio = AudioSegment.from_file(audio_path)
        
        # Создаем временный файл
        temp_path = tempfile.mktemp(suffix='.wav')
        audio.export(temp_path, format='wav')
        
        return temp_path
    
    def _send_progress(self, call_id, progress, text, segment=None):
        """
        Отправляет прогресс транскрипции через WebSocket.
        """
        try:
            async_to_sync(self.channel_layer.group_send)(
                f'transcription_{call_id}',
                {
                    'type': 'transcription_progress',
                    'call_id': str(call_id),
                    'progress': progress,
                    'text': text,
                    'segment': segment
                }
            )
        except Exception as e:
            logger.error(f"Ошибка отправки прогресса: {e}")
    
    def _send_error(self, call_id, error_message):
        """
        Отправляет сообщение об ошибке через WebSocket.
        """
        try:
            async_to_sync(self.channel_layer.group_send)(
                f'transcription_{call_id}',
                {
                    'type': 'transcription_error',
                    'call_id': str(call_id),
                    'error': error_message
                }
            )
        except Exception as e:
            logger.error(f"Ошибка отправки ошибки: {e}")


class AnalysisService:
    """
    Сервис для NLP анализа транскрипций.
    """
    
    def __init__(self):
        """Инициализирует NLP модели."""
        import spacy
        
        try:
            self.nlp_ru = spacy.load('ru_core_news_sm')
        except:
            logger.warning("Русская модель spaCy не найдена")
            self.nlp_ru = None
        
        try:
            self.nlp_en = spacy.load('en_core_web_sm')
        except:
            logger.warning("Английская модель spaCy не найдена")
            self.nlp_en = None
    
    def analyze(self, call):
        """
        Анализирует текст транскрипции звонка.
        
        Args:
            call: Объект Call для анализа
            
        Returns:
            CallAnalysis: Созданный объект анализа
        """
        from .models import CallAnalysis
        
        if not hasattr(call, 'transcription'):
            raise ValueError("Звонок не имеет транскрипции")
        
        logger.info(f"Начало анализа звонка {call.id}")
        
        text = call.transcription.text
        
        # Выбираем модель в зависимости от языка
        nlp = self.nlp_ru if call.language == 'ru' else self.nlp_en
        
        if not nlp:
            logger.warning(f"NLP модель для языка {call.language} не доступна")
            return None
        
        # Обрабатываем текст
        doc = nlp(text)
        
        # Извлекаем ключевые слова
        keywords = self._extract_keywords(doc)
        
        # Подсчитываем частоту слов
        word_frequency = self._calculate_word_frequency(text)
        
        # Определяем категорию
        category = self._classify_category(text, keywords)
        
        # Определяем тональность
        sentiment = self._analyze_sentiment(text)
        
        # Статистика говорящих (упрощенная версия)
        speaker_stats = self._analyze_speakers(call.transcription.segments)
        
        # Создаем краткое содержание
        summary = self._generate_summary(text, keywords[:5])
        
        # Создаем анализ
        analysis = CallAnalysis.objects.create(
            call=call,
            category=category,
            keywords=keywords,
            sentiment=sentiment,
            word_frequency=word_frequency,
            speaker_stats=speaker_stats,
            summary=summary
        )
        
        logger.info(f"Анализ звонка {call.id} завершен")
        
        return analysis
    
    def _extract_keywords(self, doc):
        """
        Извлекает ключевые слова из документа.
        """
        keywords = []
        
        for token in doc:
            # Фильтруем по части речи и длине
            if (token.pos_ in ['NOUN', 'PROPN', 'VERB', 'ADJ'] and
                len(token.text) > 3 and
                not token.is_stop):
                keywords.append(token.lemma_.lower())
        
        # Возвращаем топ 20 уникальных слов
        counter = Counter(keywords)
        return [word for word, count in counter.most_common(20)]
    
    def _calculate_word_frequency(self, text):
        """
        Подсчитывает частоту слов в тексте.
        """
        # Простая токенизация
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Фильтруем короткие слова
        words = [w for w in words if len(w) > 3]
        
        # Подсчитываем частоту
        counter = Counter(words)
        
        # Возвращаем топ 50
        return dict(counter.most_common(50))
    
    def _classify_category(self, text, keywords):
        """
        Классифицирует звонок по категории на основе ключевых слов.
        """
        text_lower = text.lower()
        
        # Упрощенная классификация по ключевым словам
        complaint_words = ['жалоба', 'проблема', 'плохо', 'недовольн', 'complaint', 'problem']
        order_words = ['заказ', 'купить', 'оформить', 'order', 'purchase', 'buy']
        support_words = ['помощь', 'поддержка', 'как', 'вопрос', 'help', 'support', 'question']
        
        for word in complaint_words:
            if word in text_lower:
                return 'complaint'
        
        for word in order_words:
            if word in text_lower:
                return 'order'
        
        for word in support_words:
            if word in text_lower:
                return 'support'
        
        return 'inquiry'
    
    def _analyze_sentiment(self, text):
        """
        Анализирует тональность текста (упрощенная версия).
        """
        text_lower = text.lower()
        
        positive_words = ['хорошо', 'отлично', 'спасибо', 'благодарю', 'good', 'great', 'thanks']
        negative_words = ['плохо', 'ужасно', 'проблема', 'жалоба', 'bad', 'terrible', 'problem']
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'
    
    def _analyze_speakers(self, segments):
        """
        Анализирует статистику говорящих (упрощенная версия).
        """
        if not segments:
            return {}
        
        total_duration = segments[-1]['end'] if segments else 0
        
        return {
            'total_segments': len(segments),
            'total_duration': total_duration,
            'average_segment_length': total_duration / len(segments) if segments else 0
        }
    
    def _generate_summary(self, text, top_keywords):
        """
        Генерирует краткое содержание (первые 200 символов + ключевые слова).
        """
        summary = text[:200].strip()
        if len(text) > 200:
            summary += '...'
        
        summary += f"\n\nКлючевые слова: {', '.join(top_keywords)}"
        
        return summary
