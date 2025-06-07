#!/bin/bash

# Переходим в директорию бота
cd /opt/itoq_advokat_bot || exit 1

# Проверяем наличие изменений
echo "Проверка обновлений..."
git fetch origin docker

LOCAL=$(git rev-parse HEAD)
REMOTE=$(git rev-parse origin/docker)

if [ "$LOCAL" = "$REMOTE" ]; then
    echo "Обновления не требуются"
    exit 0
fi

# Создаём резервную копию .env
echo "Создание резервной копии .env..."
cp .env .env.backup

# Останавливаем бота
echo "Остановка бота..."
docker-compose down

# Получаем обновления
echo "Получение обновлений..."
git pull origin docker

# Восстанавливаем .env
echo "Восстановление .env..."
mv .env.backup .env

# Перезапускаем бота
echo "Запуск обновленной версии..."
docker-compose up -d --build

# Проверяем статус
echo "Проверка статуса..."
docker-compose ps

echo "Обновление завершено!"
echo "Для просмотра логов выполните: docker-compose logs -f" 