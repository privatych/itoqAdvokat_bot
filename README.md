# Юридический Telegram-бот

Бот для оказания юридических консультаций и составления юридических документов с использованием AI.

## 🚀 Быстрый запуск с Docker

### Предварительные требования
- Docker и Docker Compose
- Telegram Bot Token
- OpenAI API Key

### 1. Клонирование репозитория
```bash
git clone https://github.com/your-username/itoqAdvokat_bot.git
cd itoqAdvokat_bot
```

### 2. Настройка переменных окружения
Создайте файл `.env` в корне проекта:
```bash
# Telegram Bot
BOT_TOKEN=your_telegram_bot_token

# OpenAI
OPENAI_API_KEY=your_openai_api_key

# MongoDB (опционально, если не используете Docker)
MONGODB_URI=mongodb://admin:password123@localhost:27017/legal_bot?authSource=admin

# Администраторы
ADMIN1=144739848
ADMIN2=0
```

### 3. Запуск с Docker Compose
```bash
# Сборка и запуск всех сервисов
docker-compose up -d

# Просмотр логов
docker-compose logs -f bot

# Остановка
docker-compose down
```

### 4. Проверка работоспособности
```bash
# Статус контейнеров
docker-compose ps

# Проверка health check
docker-compose exec bot python -c "print('Bot is running')"
```

## 🛠 Локальная разработка

### Установка зависимостей
```bash
python -m venv venv
source venv/bin/activate  # для Linux/Mac
# или
venv\Scripts\activate  # для Windows

pip install -r requirements.txt
```

### Запуск
```bash
python src/bot.py
```

## 📁 Структура проекта

```
├── src/
│   ├── bot.py              # Основной файл бота
│   ├── config.py           # Конфигурация
│   ├── handlers/           # Обработчики команд
│   │   ├── common.py       # Общие команды
│   │   ├── admin.py        # Админ-панель
│   │   ├── documents.py    # Работа с документами
│   │   └── consultation.py # Консультации
│   ├── services/           # Бизнес-логика
│   ├── utils/              # Вспомогательные функции
│   └── keyboards/          # Клавиатуры
├── documents/              # Генерируемые документы
├── logs/                   # Логи приложения
├── templates/              # Шаблоны документов
├── Dockerfile              # Docker образ
├── docker-compose.yml      # Docker Compose конфигурация
├── requirements.txt        # Python зависимости
└── README.md              # Документация
```

## 🔧 Функциональность

- **Юридические консультации** - получение консультаций по правовым вопросам
- **Составление документов** - автоматическое создание юридических документов
- **Админ-панель** - управление ботом и мониторинг
- **Логирование** - детальное логирование всех операций
- **База данных** - хранение пользователей и документов в MongoDB

## 🐳 Docker команды

### Управление контейнерами
```bash
# Запуск в фоновом режиме
docker-compose up -d

# Запуск с пересборкой
docker-compose up -d --build

# Остановка
docker-compose down

# Просмотр логов
docker-compose logs -f

# Перезапуск сервиса
docker-compose restart bot
```

### Резервное копирование
```bash
# Резервная копия MongoDB
docker-compose exec mongodb mongodump --out /backup

# Восстановление
docker-compose exec mongodb mongorestore /backup
```

## 🔒 Безопасность

- Все конфиденциальные данные хранятся в переменных окружения
- Использование непривилегированного пользователя в контейнере
- Изолированная сеть Docker
- Health checks для мониторинга состояния

## 📊 Мониторинг

### Логи
```bash
# Логи бота
docker-compose logs -f bot

# Логи MongoDB
docker-compose logs -f mongodb
```

### Метрики
- Health checks каждые 30 секунд
- Логирование всех операций
- Мониторинг использования ресурсов

## 🚀 Деплой

### На сервер
1. Скопируйте файлы на сервер
2. Настройте `.env` файл
3. Запустите `docker-compose up -d`

### Обновление
```bash
git pull
docker-compose down
docker-compose up -d --build
```

## 📝 Лицензия

MIT License 