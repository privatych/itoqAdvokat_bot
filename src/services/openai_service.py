from openai import AsyncOpenAI
from config import settings
from utils.logger import setup_logger

logger = setup_logger()

class OpenAIService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        logger.debug("OpenAI service initialized")

    async def get_consultation(self, user_query: str) -> str:
        """Получение юридической консультации от GPT"""
        try:
            logger.debug(f"Sending request to OpenAI with query: {user_query[:100]}...")
            
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": self._create_legal_prompt()
                    },
                    {
                        "role": "user",
                        "content": user_query
                    }
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            if not response or not response.choices:
                logger.error("OpenAI returned empty response or choices")
                raise ValueError("No response from OpenAI")
                
            answer = response.choices[0].message.content
            if not answer:
                logger.error("OpenAI returned empty content")
                raise ValueError("Empty content from OpenAI")
                
            answer = answer.strip()
            logger.debug(f"Received response from OpenAI: {answer[:100]}...")
            
            return answer
            
        except Exception as e:
            logger.error(f"Error in OpenAI consultation: {str(e)}")
            raise

    def _create_legal_prompt(self) -> str:
        """Создание системного промпта для юридической консультации"""
        return """Ты - опытный юрист-консультант в России. Твоя задача - помогать людям разбираться в юридических вопросах.

При ответе на вопросы придерживайся следующих правил:
1. Используй актуальное законодательство РФ
2. Давай четкие, структурированные ответы
3. Указывай конкретные статьи законов и нормативных актов
4. Предлагай практические шаги для решения проблемы
5. Если вопрос требует уточнения - укажи, какая информация нужна дополнительно
6. Предупреждай о возможных рисках и сложностях
7. Используй понятный язык, избегая сложных юридических терминов
8. Если требуется обращение в госорганы - укажи конкретные инстанции

Важно: Если вопрос касается уголовного права или может привести к серьезным последствиям, рекомендуй обратиться к профессиональному юристу для очной консультации."""

    async def generate_document(self, doc_type: str, details: dict) -> str:
        """Генерация юридического документа"""
        try:
            logger.debug(f"Generating document of type {doc_type} with details: {details}")
            
            # Получаем шаблон для типа документа
            templates = {
                "complaint": """
Жалоба

[Наименование органа или организации]
[Адрес]

От: [ФИО заявителя]
Адрес: [Адрес заявителя]
Телефон: [Номер телефона]

ЖАЛОБА

[Суть жалобы]

[Описание обстоятельств]

[Правовое обоснование]

На основании вышеизложенного и руководствуясь [нормативные акты], прошу:
1. [Требование]
2. [Дополнительные требования]

Приложения:
1. [Список приложенных документов]

Дата: [Дата составления]
Подпись: ____________ /[ФИО]/
                """,
                "lawsuit": """
В [Наименование суда]
[Адрес суда]

Истец: [ФИО/наименование]
Адрес: [Адрес истца]
Телефон: [Номер телефона]

Ответчик: [ФИО/наименование]
Адрес: [Адрес ответчика]

ИСКОВОЕ ЗАЯВЛЕНИЕ
[О чем]

[Описание обстоятельств дела]

[Правовое обоснование требований]

На основании изложенного и руководствуясь статьями [номера статей] ГПК РФ,

ПРОШУ:

1. [Требование]
2. [Дополнительные требования]

Цена иска: [Сумма] рублей

Приложения:
1. [Список приложенных документов]

Дата: [Дата составления]
Подпись: ____________ /[ФИО]/
                """,
                "claim": """
[Кому: наименование/ФИО]
[Адрес]

От: [ФИО/наименование]
Адрес: [Адрес заявителя]
Телефон: [Номер телефона]

ПРЕТЕНЗИЯ

[Суть претензии]

[Описание обстоятельств]

[Правовое обоснование]

На основании вышеизложенного требую:
1. [Требование]
2. [Дополнительные требования]

В случае неисполнения указанных требований в срок до [дата] буду вынужден обратиться в суд.

Приложения:
1. [Список приложенных документов]

Дата: [Дата составления]
Подпись: ____________ /[ФИО]/
                """,
                "application": """
[Кому: должность, организация]
[Адрес]

От: [ФИО заявителя]
Адрес: [Адрес заявителя]
Телефон: [Номер телефона]

ЗАЯВЛЕНИЕ

[Суть заявления]

[Описание обстоятельств]

На основании вышеизложенного прошу:
1. [Требование]
2. [Дополнительные требования]

Приложения:
1. [Список приложенных документов]

Дата: [Дата составления]
Подпись: ____________ /[ФИО]/
                """
            }
            
            # Формируем промпт для GPT
            system_prompt = """Ты - профессиональный юрист, специализирующийся на составлении юридических документов. 
            
Твоя задача - составить юридический документ на основе предоставленного шаблона и деталей.

При составлении документа:
1. Используй формальный деловой стиль
2. Следуй структуре шаблона
3. Добавляй необходимые правовые нормы и ссылки на законодательство
4. Убедись, что все важные детали из запроса пользователя включены в документ
5. Форматируй текст для удобного чтения
6. Используй актуальное законодательство РФ"""

            user_prompt = f"""Пожалуйста, составь {doc_type} на основе следующего шаблона:

{templates.get(doc_type, templates['application'])}

И следующих деталей:
{details['details']}

Замени все плейсхолдеры в шаблоне на соответствующую информацию из деталей.
Если какой-то информации не хватает - используй разумные предположения или оставь поля для заполнения в формате [ЗАПОЛНИТЬ: что именно]."""

            logger.debug(f"Sending request to OpenAI for document generation")
            
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.5,
                max_tokens=2000
            )
            
            if not response or not response.choices:
                logger.error("OpenAI returned empty response or choices")
                raise ValueError("No response from OpenAI")
            
            document = response.choices[0].message.content
            if not document:
                logger.error("OpenAI returned empty content")
                raise ValueError("Empty content from OpenAI")
                
            document = document.strip()
            logger.debug(f"Generated document: {document[:100]}...")
            
            return document
            
        except Exception as e:
            logger.error(f"Error generating document: {e}")
            raise 