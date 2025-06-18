#!/bin/bash

# Скрипт деплоя для юридического Telegram-бота
# Автор: Антон
# Версия: 2.0

set -e  # Остановка при ошибке

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функция для логирования
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

# Проверка наличия Docker
check_docker() {
    if ! command -v docker &> /dev/null; then
        error "Docker не установлен. Установите Docker и попробуйте снова."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose не установлен. Установите Docker Compose и попробуйте снова."
        exit 1
    fi
    
    log "Docker и Docker Compose найдены"
}

# Проверка файла .env
check_env() {
    if [ ! -f ".env" ]; then
        error "Файл .env не найден. Создайте его на основе env.example"
        exit 1
    fi
    
    # Проверка обязательных переменных
    source .env
    
    if [ -z "$BOT_TOKEN" ]; then
        error "BOT_TOKEN не установлен в .env файле"
        exit 1
    fi
    
    if [ -z "$OPENAI_API_KEY" ]; then
        error "OPENAI_API_KEY не установлен в .env файле"
        exit 1
    fi
    
    log "Переменные окружения проверены"
}

# Остановка существующих контейнеров
stop_containers() {
    log "Остановка существующих контейнеров..."
    docker-compose down --remove-orphans || true
}

# Сборка и запуск
build_and_start() {
    log "Сборка Docker образов..."
    docker-compose build --no-cache
    
    log "Запуск сервисов..."
    docker-compose up -d
    
    log "Ожидание запуска сервисов..."
    sleep 10
}

# Проверка статуса
check_status() {
    log "Проверка статуса сервисов..."
    
    # Проверка MongoDB
    if docker-compose exec -T mongodb mongosh --eval "db.adminCommand('ping')" > /dev/null 2>&1; then
        log "MongoDB запущен успешно"
    else
        warn "MongoDB не отвечает"
    fi
    
    # Проверка бота
    if docker-compose exec -T bot python -c "print('Bot is healthy')" > /dev/null 2>&1; then
        log "Бот запущен успешно"
    else
        warn "Бот не отвечает"
    fi
    
    # Показать статус контейнеров
    log "Статус контейнеров:"
    docker-compose ps
}

# Основная функция
main() {
    log "Начинаем деплой юридического бота..."
    
    check_docker
    check_env
    stop_containers
    build_and_start
    check_status
    
    log "Деплой завершен успешно!"
    log "Для просмотра логов используйте: docker-compose logs -f"
    log "Для остановки используйте: docker-compose down"
}

# Обработка аргументов командной строки
case "${1:-}" in
    "stop")
        log "Остановка сервисов..."
        docker-compose down
        log "Сервисы остановлены"
        ;;
    "restart")
        log "Перезапуск сервисов..."
        docker-compose restart
        log "Сервисы перезапущены"
        ;;
    "logs")
        log "Показать логи..."
        docker-compose logs -f
        ;;
    "status")
        check_status
        ;;
    "update")
        log "Обновление из Git..."
        git pull
        main
        ;;
    *)
        main
        ;;
esac 