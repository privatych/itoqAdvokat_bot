from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from utils.logger import setup_logger
from services.user_service import register_user

logger = setup_logger()
router = Router()

def get_main_keyboard():
    """Создает основную клавиатуру"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📝 Получить консультацию"),
                KeyboardButton(text="📄 Создать документ")
            ],
            [
                KeyboardButton(text="❓ Помощь"),
                KeyboardButton(text="ℹ️ О боте")
            ]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите действие"
    )
    return keyboard

@router.message(Command("start"))
async def cmd_start(message: Message):
    """
    Обработчик команды /start
    """
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    
    # Регистрируем пользователя
    await register_user(user_id, username, first_name)
    logger.info(f"User {user_id} started the bot")
    
    await message.answer(
        "👋 Здравствуйте! Я бот-юрист, готовый помочь вам с юридическими вопросами.\n\n"
        "Что я умею:\n"
        "📝 Консультации по юридическим вопросам\n"
        "📄 Помощь в составлении документов\n\n"
        "Выберите нужное действие на клавиатуре или используйте команду /help для справки.",
        reply_markup=get_main_keyboard()
    )

@router.message(Command("help"))
async def cmd_help(message: Message):
    """
    Обработчик команды /help
    """
    help_text = """
📚 Доступные команды:

🔹 Получить консультацию - юридическая консультация по любому вопросу
🔹 Создать документ - помощь в составлении юридических документов

💡 Как пользоваться:
1. Выберите нужный раздел на клавиатуре
2. Следуйте инструкциям бота
3. Для отмены операции используйте команду /cancel

⚠️ Важно:
- Будьте точны в описании ситуации
- Указывайте все существенные детали
- При необходимости прикрепляйте документы
    """
    await message.answer(help_text, reply_markup=get_main_keyboard())
    logger.info(f"User {message.from_user.id} requested help")

@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    """
    Обработчик команды /cancel
    """
    current_state = await state.get_state()
    user_id = message.from_user.id
    
    if current_state is not None:
        logger.info(f"User {user_id} cancelled operation from state {current_state}")
        await state.clear()
        await message.answer(
            "❌ Текущая операция отменена. Выберите новое действие:",
            reply_markup=get_main_keyboard()
        )
    else:
        logger.debug(f"User {user_id} tried to cancel with no active state")
        await message.answer(
            "🤔 У вас нет активной операции",
            reply_markup=get_main_keyboard()
        )



@router.message(F.text == "❓ Помощь")
async def handle_help_button(message: Message):
    """Обработчик кнопки помощи"""
    await cmd_help(message)

@router.message(F.text == "ℹ️ О боте")
async def handle_about_button(message: Message):
    """Обработчик кнопки о боте"""
    about_text = """
🤖 Юридический ассистент

Я специализируюсь на предоставлении юридических консультаций и помощи в составлении документов по российскому законодательству.

✅ Мои возможности:
- Консультации по различным отраслям права
- Составление юридических документов
- Разъяснение законодательства
- Помощь в подготовке обращений

⚖️ Области права:
- Гражданское право
- Административное право
- Трудовое право
- Семейное право
- Защита прав потребителей

📝 Для начала работы выберите нужный раздел на клавиатуре
    """
    await message.answer(about_text, reply_markup=get_main_keyboard())
    logger.info(f"User {message.from_user.id} requested bot info") 