from typing import Optional, Dict
from aiogram import Bot
from aiogram.types import FSInputFile
import asyncio
from utils.logger import setup_logger
from services.user_service import get_all_users, set_user_active_status

logger = setup_logger()

async def send_message_to_user(
    bot: Bot,
    user_id: int,
    text: str,
    photo: Optional[FSInputFile] = None,
    video: Optional[FSInputFile] = None
) -> bool:
    """
    Отправляет сообщение конкретному пользователю
    Возвращает True если сообщение успешно отправлено
    """
    try:
        if photo:
            await bot.send_photo(chat_id=user_id, photo=photo, caption=text)
        elif video:
            await bot.send_video(chat_id=user_id, video=video, caption=text)
        else:
            await bot.send_message(chat_id=user_id, text=text)
        return True
    except Exception as e:
        logger.error(f"Error sending message to user {user_id}: {e}")
        return False

async def broadcast_message(
    bot: Bot,
    text: str,
    photo: Optional[FSInputFile] = None,
    video: Optional[FSInputFile] = None
) -> Dict:
    """
    Выполняет рассылку сообщения всем пользователям
    Возвращает статистику рассылки
    """
    users = await get_all_users()
    total_users = len(users)
    successful = 0
    failed = 0

    for user_id, is_active in users:
        if not is_active:
            continue

        success = await send_message_to_user(bot, user_id, text, photo, video)
        
        if success:
            successful += 1
        else:
            failed += 1
            # Если сообщение не удалось отправить, помечаем пользователя как неактивного
            await set_user_active_status(user_id, False)
        
        # Небольшая задержка между отправками
        await asyncio.sleep(0.1)

    return {
        "total": total_users,
        "successful": successful,
        "failed": failed
    } 