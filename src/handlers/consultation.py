from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from services.openai_service import OpenAIService
from handlers.common import get_main_keyboard
from utils.logger import setup_logger

logger = setup_logger()
router = Router()

class ConsultationStates(StatesGroup):
    waiting_for_question = State()

@router.message(Command("consult"))
@router.message(F.text == "📝 Получить консультацию")
async def start_consultation(message: Message, state: FSMContext):
    """Начало процесса консультации"""
    user_id = message.from_user.id
    logger.info(f"User {user_id} starting consultation process")
    
    try:
        # Очищаем предыдущее состояние
        current_state = await state.get_state()
        if current_state:
            logger.debug(f"Clearing previous state {current_state} for user {user_id}")
            await state.clear()
        
        # Устанавливаем новое состояние
        await state.set_state(ConsultationStates.waiting_for_question)
        logger.debug(f"Set state to waiting_for_question for user {user_id}")
        
        await message.answer(
            "🤝 Готов помочь с юридической консультацией!\n\n"
            "Пожалуйста, опишите вашу ситуацию максимально подробно.\n"
            "Укажите важные детали:\n"
            "- Даты событий\n"
            "- Суммы (если есть)\n"
            "- Участников\n"
            "- Что уже было сделано\n"
            "- Какой результат хотите получить\n\n"
            "Для отмены используйте команду /cancel",
            reply_markup=ReplyKeyboardRemove()
        )
        
    except Exception as e:
        logger.error(f"Error in start_consultation for user {user_id}: {e}")
        await message.answer(
            "😔 Произошла ошибка при начале консультации. Пожалуйста, попробуйте позже.",
            reply_markup=get_main_keyboard()
        )
        await state.clear()

@router.message(StateFilter(ConsultationStates.waiting_for_question))
async def process_question(message: Message, state: FSMContext):
    """Обработка вопроса пользователя"""
    user_id = message.from_user.id
    logger.info(f"Processing question from user {user_id}")
    
    try:
        if not message.text:
            logger.warning(f"User {user_id} sent non-text message")
            await message.answer(
                "⚠️ Пожалуйста, отправьте ваш вопрос текстовым сообщением."
            )
            return

        # Отправляем сообщение о начале обработки
        processing_msg = await message.answer("⏳ Анализирую ваш вопрос...")
        logger.debug(f"Question from user {user_id}: {message.text[:100]}...")

        # Инициализируем сервис OpenAI
        openai_service = OpenAIService()
        
        # Получаем ответ от OpenAI
        try:
            response = await openai_service.get_consultation(message.text)
            logger.debug(f"Received response from OpenAI for user {user_id}: {response[:100]}...")
            
            if not response or response.isspace():
                raise ValueError("Empty response from OpenAI")
                
            # Форматируем и отправляем ответ
            formatted_response = f"""
📋 Юридическая консультация:

{response}

❓ Есть ли у вас дополнительные вопросы?
Выберите действие на клавиатуре ниже:
            """
            
            # Удаляем сообщение о обработке
            await processing_msg.delete()
            
            # Отправляем ответ
            await message.answer(formatted_response, reply_markup=get_main_keyboard())
            logger.info(f"Successfully sent consultation response to user {user_id}")
            
            # Сбрасываем состояние
            await state.clear()
            logger.debug(f"Cleared state for user {user_id}")
            
        except Exception as e:
            logger.error(f"OpenAI service error for user {user_id}: {e}")
            await processing_msg.delete()
            await message.answer(
                "😔 Извините, произошла ошибка при обработке вашего вопроса.\n"
                "Пожалуйста, попробуйте переформулировать вопрос или начните сначала.",
                reply_markup=get_main_keyboard()
            )
            
    except Exception as e:
        logger.error(f"Error in process_question for user {user_id}: {e}")
        await message.answer(
            "😔 Произошла ошибка при обработке вашего вопроса.\n"
            "Пожалуйста, попробуйте позже или обратитесь к администратору.",
            reply_markup=get_main_keyboard()
        )
        await state.clear()

@router.message(Command("cancel"))
async def cancel_consultation(message: Message, state: FSMContext):
    """Отмена текущей консультации"""
    user_id = message.from_user.id
    logger.info(f"User {user_id} cancelling consultation")
    
    try:
        current_state = await state.get_state()
        if current_state is not None:
            await state.clear()
            logger.debug(f"Cleared state {current_state} for user {user_id}")
            await message.answer(
                "❌ Консультация отменена.\n"
                "Вы можете начать новую консультацию в любое время.",
                reply_markup=get_main_keyboard()
            )
        else:
            logger.debug(f"No active consultation to cancel for user {user_id}")
            await message.answer(
                "🤔 У вас нет активной консультации для отмены.",
                reply_markup=get_main_keyboard()
            )
    except Exception as e:
        logger.error(f"Error cancelling consultation for user {user_id}: {e}")
        await message.answer(
            "Произошла ошибка при отмене консультации",
            reply_markup=get_main_keyboard()
        ) 