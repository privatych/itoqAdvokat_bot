# Юридический Telegram-бот

Бот для оказания юридических консультаций и составления юридических документов.

## Установка

1. Клонируйте репозиторий:
```bash
git clone [url-репозитория]
cd [название-директории]
```

2. Создайте виртуальное окружение и активируйте его:
```bash
python -m venv venv
source venv/bin/activate  # для Linux/Mac
# или
venv\Scripts\activate  # для Windows
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Создайте файл .env и заполните его необходимыми данными:
```
BOT_TOKEN=your_telegram_bot_token
OPENAI_API_KEY=your_openai_api_key
MONGODB_URI=mongodb://localhost:27017
DATABASE_NAME=legal_bot
```

## Запуск

```bash
python src/bot.py
```

## Функциональность

- Юридические консультации
- Составление юридических документов
- Поддержка различных областей права
- Интеграция с GPT для обработки запросов

## Структура проекта

```
├── src/
│   ├── bot.py          # Основной файл бота
│   ├── config.py       # Конфигурация
│   ├── handlers/       # Обработчики команд
│   ├── services/       # Бизнес-логика
│   └── utils/          # Вспомогательные функции
├── requirements.txt    # Зависимости
└── README.md          # Документация
``` 