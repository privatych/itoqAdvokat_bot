import asyncio
import logging
import signal
import sys
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from config import settings
from handlers.common import router as common_router
from handlers.admin import admin_router
from handlers.documents import router as documents_router
from handlers.consultation import router as consultation_router
from utils.logger import setup_logger

# Настройка логгера
logger = setup_logger()

# Глобальные переменные для управления состоянием бота
bot = Bot(token=settings.BOT_TOKEN, parse_mode="HTML")
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

async def set_commands(bot: Bot):
    """Установка команд бота"""
    commands = [
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="help", description="Помощь"),
        BotCommand(command="cancel", description="Отменить текущую операцию"),
        BotCommand(command="admin", description="Админ-панель")
    ]
    await bot.set_my_commands(commands)
    logger.info("Bot commands have been set")

async def on_shutdown(dispatcher: Dispatcher, bot: Bot):
    """Действия при выключении бота"""
    logger.info("Shutting down bot...")
    await bot.session.close()
    logger.info("Bot shutdown completed")

async def main():
    """Основная функция запуска бота"""
    logger.info("Starting bot initialization")
    
    # Регистрация роутеров
    dp.include_router(common_router)
    dp.include_router(documents_router)
    dp.include_router(consultation_router)
    dp.include_router(admin_router)
    
    # Установка команд бота
    await set_commands(bot)
    
    # Настройка обработки сигналов завершения
    async def handle_shutdown(signal_type):
        logger.info(f"Received shutdown signal: {signal_type}")
        await on_shutdown(dp, bot)
        sys.exit(0)

    for sig in (signal.SIGINT, signal.SIGTERM):
        asyncio.get_event_loop().add_signal_handler(
            sig,
            lambda s=sig: asyncio.create_task(handle_shutdown(s))
        )
    
    # Запуск процесса поллинга
    logger.info("Starting bot polling")
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await on_shutdown(dp, bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise 