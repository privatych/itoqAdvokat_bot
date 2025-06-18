// Инициализация базы данных для юридического бота
db = db.getSiblingDB('legal_bot');

// Создание пользователя для базы данных
db.createUser({
  user: 'bot_user',
  pwd: 'bot_password',
  roles: [
    {
      role: 'readWrite',
      db: 'legal_bot'
    }
  ]
});

// Создание коллекций
db.createCollection('users');
db.createCollection('documents');
db.createCollection('consultations');
db.createCollection('logs');

// Создание индексов для оптимизации
db.users.createIndex({ "user_id": 1 }, { unique: true });
db.documents.createIndex({ "user_id": 1, "created_at": -1 });
db.consultations.createIndex({ "user_id": 1, "created_at": -1 });

print('MongoDB initialized successfully'); 