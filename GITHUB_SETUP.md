# Настройка GitHub для автоматического деплоя

## 1. Создание репозитория

1. Перейдите на [GitHub](https://github.com)
2. Создайте новый репозиторий: `itoqAdvokat_bot`
3. Сделайте его приватным (рекомендуется для ботов)

## 2. Инициализация Git и первый коммит

```bash
# Инициализация Git (если еще не сделано)
git init

# Добавление всех файлов
git add .

# Первый коммит
git commit -m "Initial commit: Legal Telegram Bot with Docker"

# Добавление удаленного репозитория
git remote add origin https://github.com/YOUR_USERNAME/itoqAdvokat_bot.git

# Отправка в GitHub
git push -u origin main
```

## 3. Настройка GitHub Secrets

Для автоматического деплоя нужно настроить секреты в репозитории:

1. Перейдите в Settings → Secrets and variables → Actions
2. Добавьте следующие секреты:

### Обязательные секреты:
- `HOST` - IP адрес вашего сервера
- `USERNAME` - имя пользователя на сервере
- `SSH_KEY` - приватный SSH ключ для доступа к серверу
- `PORT` - SSH порт (обычно 22)
- `DEPLOY_PATH` - путь к директории на сервере (например: `/home/user/bot`)

### Пример настройки SSH ключа:
```bash
# Генерация SSH ключа (если нет)
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"

# Копирование публичного ключа на сервер
ssh-copy-id user@your-server-ip

# Приватный ключ (содержимое ~/.ssh/id_rsa) нужно добавить в GitHub Secrets
cat ~/.ssh/id_rsa
```

## 4. Настройка сервера

### Установка Docker на сервер:
```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Установка Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Создание директории для бота:
```bash
mkdir -p /home/user/bot
cd /home/user/bot
```

### Клонирование репозитория:
```bash
git clone https://github.com/YOUR_USERNAME/itoqAdvokat_bot.git .
```

### Создание .env файла:
```bash
cp env.example .env
nano .env
# Заполните все необходимые переменные
```

## 5. Тестирование деплоя

После настройки всех секретов:

1. Сделайте изменения в коде
2. Запушьте в main ветку:
```bash
git add .
git commit -m "Test deployment"
git push origin main
```

3. Проверьте GitHub Actions:
   - Перейдите в Actions вкладку репозитория
   - Убедитесь, что workflow выполнился успешно

## 6. Мониторинг

### Просмотр логов на сервере:
```bash
cd /home/user/bot
docker-compose logs -f bot
```

### Проверка статуса:
```bash
docker-compose ps
```

### Перезапуск при необходимости:
```bash
docker-compose restart bot
```

## 7. Безопасность

### Рекомендации:
- Используйте приватный репозиторий
- Регулярно обновляйте SSH ключи
- Используйте firewall на сервере
- Регулярно обновляйте Docker и систему
- Делайте резервные копии данных

### Резервное копирование:
```bash
# Резервная копия MongoDB
docker-compose exec mongodb mongodump --out /backup

# Резервная копия файлов
tar -czf backup-$(date +%Y%m%d).tar.gz /home/user/bot
```

## 8. Устранение неполадок

### Проблемы с SSH:
```bash
# Проверка подключения
ssh -T user@your-server-ip

# Проверка прав на ключ
chmod 600 ~/.ssh/id_rsa
```

### Проблемы с Docker:
```bash
# Очистка Docker
docker system prune -a

# Перезапуск Docker
sudo systemctl restart docker
```

### Проблемы с ботом:
```bash
# Просмотр логов
docker-compose logs bot

# Перезапуск контейнера
docker-compose restart bot
``` 