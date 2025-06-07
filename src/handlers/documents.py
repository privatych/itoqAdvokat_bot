from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, FSInputFile
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from services.openai_service import OpenAIService
from services.document_service import DocumentService
from handlers.common import get_main_keyboard
from utils.logger import setup_logger

logger = setup_logger()
router = Router()

# Инициализируем сервисы
openai_service = OpenAIService()
document_service = DocumentService()

class DocumentStates(StatesGroup):
    selecting_type = State()
    filling_details = State()

# Словарь для хранения данных документа во время заполнения
document_data = {}

@router.message(Command("document"))
@router.message(F.text == "📄 Создать документ")
async def start_document_creation(message: Message, state: FSMContext):
    """Начало процесса создания документа"""
    user_id = message.from_user.id
    logger.info(f"User {user_id} starting document creation")
    
    try:
        # Очищаем предыдущее состояние
        current_state = await state.get_state()
        if current_state:
            logger.debug(f"Clearing previous state {current_state} for user {user_id}")
            await state.clear()
        
        # Устанавливаем новое состояние
        await state.set_state(DocumentStates.selecting_type)
        logger.debug(f"Set state to selecting_type for user {user_id}")
        
        # Создаем клавиатуру с типами документов
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="📝 Жалоба"),
                    KeyboardButton(text="⚖️ Иск")
                ],
                [
                    KeyboardButton(text="📋 Претензия"),
                    KeyboardButton(text="📄 Заявление")
                ],
                [
                    KeyboardButton(text="❌ Отмена")
                ]
            ],
            resize_keyboard=True
        )
        
        await message.answer(
            "📋 Выберите тип документа:\n\n"
            "📝 Жалоба - обращение в государственные органы\n"
            "⚖️ Иск - заявление в суд\n"
            "📋 Претензия - досудебное урегулирование\n"
            "📄 Заявление - общего характера\n\n"
            "❌ Отмена - вернуться в главное меню",
            reply_markup=keyboard
        )
        
    except Exception as e:
        logger.error(f"Error in start_document_creation for user {user_id}: {e}")
        await message.answer(
            "😔 Произошла ошибка при начале создания документа. Пожалуйста, попробуйте позже.",
            reply_markup=get_main_keyboard()
        )
        await state.clear()

@router.message(StateFilter(DocumentStates.selecting_type))
async def process_document_type(message: Message, state: FSMContext):
    """Обработка выбора типа документа"""
    user_id = message.from_user.id
    logger.info(f"Processing document type selection from user {user_id}")
    
    try:
        if message.text == "❌ Отмена":
            await state.clear()
            await message.answer(
                "❌ Создание документа отменено.",
                reply_markup=get_main_keyboard()
            )
            return
            
        # Проверяем корректность выбора типа документа
        doc_types = {
            "📝 Жалоба": "complaint",
            "⚖️ Иск": "lawsuit",
            "📋 Претензия": "claim",
            "📄 Заявление": "application"
        }
        
        if message.text not in doc_types:
            await message.answer(
                "⚠️ Пожалуйста, выберите тип документа из предложенных вариантов."
            )
            return
            
        # Сохраняем тип документа
        await state.update_data(doc_type=doc_types[message.text])
        
        # Переходим к заполнению деталей
        await state.set_state(DocumentStates.filling_details)
        
        # Запрашиваем детали в зависимости от типа документа
        prompts = {
            "complaint": (
                "Для составления жалобы, пожалуйста, укажите:\n"
                "1. В какой орган направляется жалоба\n"
                "2. На что/кого жалуетесь\n"
                "3. Что произошло (даты, события)\n"
                "4. Какие права нарушены\n"
                "5. Чего хотите добиться"
            ),
            "lawsuit": (
                "Для составления иска, пожалуйста, укажите:\n"
                "1. Данные ответчика\n"
                "2. Суть требований\n"
                "3. Обстоятельства дела\n"
                "4. Правовое обоснование\n"
                "5. Цена иска (если есть)"
            ),
            "claim": (
                "Для составления претензии, пожалуйста, укажите:\n"
                "1. Кому направляется претензия\n"
                "2. Суть претензии\n"
                "3. Что произошло\n"
                "4. Ваши требования\n"
                "5. Сроки исполнения"
            ),
            "application": (
                "Для составления заявления, пожалуйста, укажите:\n"
                "1. Кому направляется заявление\n"
                "2. Суть обращения\n"
                "3. Что просите сделать\n"
                "4. Дополнительные сведения"
            )
        }
        
        doc_type = doc_types[message.text]
        await message.answer(
            f"📝 {prompts[doc_type]}\n\n"
            "Для отмены используйте команду /cancel",
            reply_markup=ReplyKeyboardRemove()
        )
        
    except Exception as e:
        logger.error(f"Error in process_document_type for user {user_id}: {e}")
        await message.answer(
            "😔 Произошла ошибка при обработке типа документа.\n"
            "Пожалуйста, попробуйте позже или начните сначала.",
            reply_markup=get_main_keyboard()
        )
        await state.clear()

@router.message(StateFilter(DocumentStates.filling_details))
async def process_document_details(message: Message, state: FSMContext):
    """Обработка деталей документа"""
    user_id = message.from_user.id
    logger.info(f"Processing document details from user {user_id}")
    
    try:
        if not message.text:
            logger.warning(f"User {user_id} sent non-text message")
            await message.answer(
                "⚠️ Пожалуйста, отправьте информацию текстовым сообщением."
            )
            return

        # Отправляем сообщение о начале обработки
        processing_msg = await message.answer("⏳ Составляю документ...")
        logger.debug(f"Document details from user {user_id}: {message.text[:100]}...")

        # Получаем сохраненные данные
        user_data = await state.get_data()
        doc_type = user_data.get("doc_type")
        
        if not doc_type:
            raise ValueError("Document type not found in state data")

        try:
            # Генерируем документ через OpenAI
            document_text = await openai_service.generate_document(doc_type, {
                "details": message.text
            })
            
            if not document_text or document_text.isspace():
                raise ValueError("Empty document generated")
            
            # Создаем Word документ
            doc_path = document_service.create_docx(document_text, user_id, doc_type)
            
            # Отправляем файл пользователю
            doc = FSInputFile(doc_path)
            await message.answer_document(
                document=doc,
                caption="📄 Ваш документ готов!\n\nВы можете отредактировать его под свои нужды.\nДля создания нового документа нажмите «📄 Создать документ»",
                reply_markup=get_main_keyboard()
            )
            
            # Удаляем сообщение о обработке
            await processing_msg.delete()
            
            # Сбрасываем состояние
            await state.clear()
            logger.info(f"Successfully generated document for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error generating document for user {user_id}: {e}")
            await processing_msg.delete()
            await message.answer(
                "😔 Извините, произошла ошибка при составлении документа.\n"
                "Пожалуйста, попробуйте еще раз или начните сначала.",
                reply_markup=get_main_keyboard()
            )
            await state.clear()
            
    except Exception as e:
        logger.error(f"Error in process_document_details for user {user_id}: {e}")
        await message.answer(
            "😔 Произошла ошибка при обработке деталей документа.\n"
            "Пожалуйста, попробуйте позже или обратитесь к администратору.",
            reply_markup=get_main_keyboard()
        )
        await state.clear()

@router.message(Command("cancel"))
async def cancel_document(message: Message, state: FSMContext):
    """Отмена создания документа"""
    user_id = message.from_user.id
    logger.info(f"User {user_id} cancelling document creation")
    
    try:
        current_state = await state.get_state()
        if current_state is not None:
            await state.clear()
            logger.debug(f"Cleared state {current_state} for user {user_id}")
            await message.answer(
                "❌ Создание документа отменено.\n"
                "Вы можете начать создание нового документа в любое время.",
                reply_markup=get_main_keyboard()
            )
        else:
            logger.debug(f"No active document creation to cancel for user {user_id}")
            await message.answer(
                "🤔 У вас нет активного процесса создания документа.",
                reply_markup=get_main_keyboard()
            )
    except Exception as e:
        logger.error(f"Error cancelling document creation for user {user_id}: {e}")
        await message.answer(
            "Произошла ошибка при отмене создания документа",
            reply_markup=get_main_keyboard()
        ) 