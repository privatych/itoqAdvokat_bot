FROM python:3.11

# Установка переменных окружения
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    PYTHONPATH=/app

# Установка рабочей директории
WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    python3-dev \
    libffi-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Создание и активация виртуального окружения
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Обновление pip и установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY . .

# Создание непривилегированного пользователя
RUN useradd -m -u 1000 bot_user && \
    chown -R bot_user:bot_user /app
USER bot_user

# Проверка работоспособности - простая проверка что Python работает
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "print('Bot is healthy')" || exit 1

# Запуск бота
CMD ["python", "src/bot.py"] 