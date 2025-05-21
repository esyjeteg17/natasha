import tempfile
import json
import nltk
from nltk.data import find
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import APIException, ValidationError

from gigachat import GigaChat
from gigachat.api.utils import ResponseError
from docx import Document as DocxDocument

from .serializers import DocumentSerializer
from .extract_keywords import get_keywords_and_topic


class DocumentReviewViewSet(viewsets.GenericViewSet,
                            viewsets.mixins.CreateModelMixin):
    """
    POST /api/doc-review/
    Принимает .docx-файл и тему из фронтенда,
    сжимает текст, отправляет в GigaChat и возвращает:
      - ответ нейронки,
      - ключевые слова с количеством вхождений,
      - извлечённую тему,
      - общее количество слов в документе,
      - boolean passed.
    """
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAuthenticated]
    serializer_class = DocumentSerializer

    MAX_CHARS = 3000  # порог для части текста при сжатии

    def extract_full_text(self, path):
        doc = DocxDocument(path)
        full_text = []
        for para in doc.paragraphs:
            text = para.text.strip()
            if text:
                full_text.append(text)
        return "\n".join(full_text)

    def compress_text(self, text, giga):
        if len(text) <= self.MAX_CHARS:
            return text
        chunks = [text[i:i + self.MAX_CHARS] for i in range(0, len(text), self.MAX_CHARS)]
        compressed = []
        for idx, chunk in enumerate(chunks, start=1):
            prompt = (
                f"Сожми следующий текст до краткого содержательного резюме, "
                f"сообщи только основные идеи (часть {idx}/{len(chunks)}):\n" + chunk
            )
            try:
                resp = giga.chat(prompt)
            except ResponseError as e:
                raise APIException(f"Ошибка при сжатии текста: {e}")
            compressed.append(resp.choices[0].message.content)
        combined = "\n".join(compressed)
        return self.compress_text(combined, giga)

    def create(self, request, *args, **kwargs):
        # 1) валидация файла
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        uploaded_file = serializer.validated_data['file']

        # 2) получение темы из фронтенда
        topic = request.data.get('topic')
        if not topic:
            raise ValidationError({'topic': 'Это поле обязательно.'})

        # 3) сохранить файл во временный .docx
        with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
            for chunk in uploaded_file.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name

        # 4) извлечение полного текста и подсчёт слов
        full_text = self.extract_full_text(tmp_path)
        word_count = len(full_text.split())

        # 5) проверяем и скачиваем стоп-слова NLTK, если нужно
        try:
            find('corpora/stopwords')
        except LookupError:
            # на macOS/других может потребоваться отключить проверку SSL для загрузки
            import ssl
            try:
                _create_unverified_https_context = ssl._create_unverified_context
            except AttributeError:
                pass
            else:
                ssl._create_default_https_context = _create_unverified_https_context
            nltk.download('stopwords', quiet=True)

        # 6) извлечение ключевых слов и темы из документа) извлечение ключевых слов и темы из документа
        top_words, extracted_topic = get_keywords_and_topic(tmp_path, top_n=5)
        keywords_data = [{"keyword": w, "count": c} for w, c in top_words]

        # 7) подготовка к запросам GigaChat
        creds = getattr(settings, 'GIGACHAT_CREDENTIALS', None)
        if not creds:
            raise APIException("Не задана настройка GIGACHAT_CREDENTIALS")
        verify_ssl = getattr(settings, 'GIGACHAT_VERIFY_SSL', True)

        try:
            with GigaChat(credentials=creds, verify_ssl_certs=verify_ssl) as giga:
                compressed = self.compress_text(full_text, giga)

                # первый запрос: развёрнутая оценка
                eval_prompt = (
                    f"Оцени работу студента по теме '{topic}'.\n"
                    f"Вот резюме его текста:\n{compressed}\n"
                    "Дай подробный развёрнутый ответ без JSON."
                )
                resp_eval = giga.chat(eval_prompt)
                raw_evaluation = resp_eval.choices[0].message.content.strip()

                # второй запрос: проверка соответствия теме
                pass_prompt = (
                    f"Тема документа: '{topic}'.\n"
                    f"Краткое содержание документа:\n{compressed}\n"
                    "На основе указанной темы и содержания, "
                    "ответь одним словом true, если содержание соответствует теме, иначе false."
                )
                resp_pass = giga.chat(pass_prompt)
                raw_pass = resp_pass.choices[0].message.content.strip().lower()
        except ResponseError as e:
            raise APIException(f"Ошибка GigaChat API: {e}")
        except Exception as e:
            raise APIException(f"Ошибка при обращении к GigaChat: {e}")

        # 8) парсинг passed
        passed = True if raw_pass == 'true' else False

        # 9) возвращаем фронтенду
        return Response({
            "evaluation": raw_evaluation,
            "keywords": keywords_data,
            "extracted_topic": extracted_topic,
            "word_count": word_count,
            "passed": passed,
        }, status=status.HTTP_200_OK)
