# Инструкция по развертыванию бота

## Подготовка сервера

1. Установите Docker и Docker Compose:
```bash
# Обновление пакетов
sudo apt update
sudo apt upgrade -y

# Установка необходимых пакетов
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

# Добавление Docker GPG ключа
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -

# Добавление репозитория Docker
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"

# Установка Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io

# Установка Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

2. Создайте рабочую директорию:
```bash
mkdir -p /opt/itoq_advokat_bot
cd /opt/itoq_advokat_bot
```

## Развертывание бота

1. Скопируйте файлы проекта на сервер:
```bash
# Локально выполните:
scp -r ./* user@your-server:/opt/itoq_advokat_bot/
```

2. Создайте файл с переменными окружения:
```bash
# На сервере создайте файл .env:
nano .env

# Добавьте необходимые переменные:
BOT_TOKEN=ваш_токен_бота
OPENAI_API_KEY=ваш_ключ_openai
ADMIN_USER_ID=ваш_telegram_id
# Опционально:
MONGODB_URI=ваш_uri_mongodb
```

3. Запустите бота:
```bash
cd /opt/itoq_advokat_bot
sudo docker-compose up -d --build
```

## Управление ботом

- Просмотр логов:
```bash
docker-compose logs -f
```

- Перезапуск бота:
```bash
docker-compose restart
```

- Остановка бота:
```bash
docker-compose down
```

- Обновление бота:
```bash
# Остановите контейнеры
docker-compose down

# Получите обновления (если используете git)
git pull

# Или скопируйте новые файлы
# scp -r ./* user@your-server:/opt/itoq_advokat_bot/

# Пересоберите и запустите
docker-compose up -d --build
```

## Мониторинг

1. Проверка статуса:
```bash
docker ps
```

2. Проверка использования ресурсов:
```bash
docker stats itoq_advokat_bot
```

## Безопасность

1. Убедитесь, что файл .env имеет правильные права доступа:
```bash
chmod 600 .env
```

2. Регулярно обновляйте систему и Docker:
```bash
sudo apt update && sudo apt upgrade -y
sudo docker-compose pull
``` 