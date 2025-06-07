import os
from pathlib import Path
from dotenv import load_dotenv
from utils.logger import setup_logger
from pydantic_settings import BaseSettings
from typing import Optional

logger = setup_logger()

# Определяем путь к файлу .env
env_path = Path(__file__).parent.parent / '.env'

# Загружаем переменные окружения из .env файла
if env_path.exists():
    load_dotenv(env_path)
    logger.info(f"Loaded environment variables from {env_path}")
else:
    logger.warning(f"Environment file not found at {env_path}")

class Settings(BaseSettings):
    """Класс для хранения настроек приложения"""
    
    BOT_TOKEN: str
    OPENAI_API_KEY: str
    MONGODB_URI: Optional[str] = None  # Делаем опциональным
    
    # ID администраторов
    ADMIN1: int = 144739848  # Ваш ID
    ADMIN2: int = 0  # Второй админ, если нужен
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Создаем экземпляр настроек
settings = Settings()
logger.info("Settings initialized successfully")

# Экспортируем переменные для использования в других модулях
BOT_TOKEN = settings.BOT_TOKEN
OPENAI_API_KEY = settings.OPENAI_API_KEY
MONGODB_URI = settings.MONGODB_URI
ADMIN1 = settings.ADMIN1
ADMIN2 = settings.ADMIN2
ADMIN_ID = 144739848  # Устанавливаем ID напрямую для отладки

# Проверка обязательных переменных
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set in environment variables") 