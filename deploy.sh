#!/bin/bash

# Проверка наличия аргументов
if [ "$#" -ne 2 ]; then
    echo "Использование: $0 user@server /path/to/deploy"
    exit 1
fi

SERVER=$1
DEPLOY_PATH=$2

echo "Начинаю развертывание бота на сервере $SERVER в директорию $DEPLOY_PATH"

# Создание директории на сервере
echo "Создание директории на сервере..."
ssh $SERVER "mkdir -p $DEPLOY_PATH"

# Копирование файлов
echo "Копирование файлов проекта..."
scp -r ./* $SERVER:$DEPLOY_PATH/

# Установка прав
echo "Настройка прав доступа..."
ssh $SERVER "chmod 600 $DEPLOY_PATH/.env"

# Запуск бота
echo "Запуск бота..."
ssh $SERVER "cd $DEPLOY_PATH && docker-compose up -d --build"

# Проверка статуса
echo "Проверка статуса..."
ssh $SERVER "cd $DEPLOY_PATH && docker-compose ps"

echo "Развертывание завершено!"
echo "Для просмотра логов выполните:"
echo "ssh $SERVER 'cd $DEPLOY_PATH && docker-compose logs -f'" 