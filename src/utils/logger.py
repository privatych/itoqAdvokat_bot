import logging
import sys
from logging.handlers import RotatingFileHandler

def setup_logger():
    # Создаем логгер
    logger = logging.getLogger('bot_logger')
    logger.setLevel(logging.DEBUG)

    # Форматирование логов
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Хендлер для записи в файл
    file_handler = RotatingFileHandler(
        'bot.log',
        maxBytes=10485760,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Хендлер для вывода в консоль
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # Добавляем хендлеры к логгеру
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger 