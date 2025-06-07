from typing import Dict, List, Tuple
from pymongo import MongoClient
from config import MONGODB_URI
from utils.logger import setup_logger

logger = setup_logger()

# Инициализация MongoDB только если есть URI
if MONGODB_URI:
    try:
        client = MongoClient(MONGODB_URI)
        db = client.get_database('bot_db')
        users_collection = db.get_collection('users')
        logger.info("Successfully connected to MongoDB")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        users_collection = None
else:
    logger.warning("MONGODB_URI not provided, running without database")
    users_collection = None

# Создаем локальное хранилище для работы без MongoDB
local_users = {}

async def register_user(user_id: int, username: str = None, first_name: str = None) -> None:
    """Регистрирует нового пользователя или обновляет информацию о существующем"""
    user_data = {
        'user_id': user_id,
        'username': username,
        'first_name': first_name,
        'is_active': True,
        'used_start_promo': False
    }
    
    if users_collection:
        try:
            users_collection.update_one(
                {'user_id': user_id},
                {'$set': user_data},
                upsert=True
            )
            logger.info(f"User {user_id} registered/updated in MongoDB")
        except Exception as e:
            logger.error(f"Error registering user in MongoDB: {e}")
    else:
        local_users[user_id] = user_data
        logger.info(f"User {user_id} registered/updated in local storage")

async def get_all_users() -> List[Tuple[int, bool]]:
    """Получает список всех пользователей"""
    if users_collection:
        try:
            users = users_collection.find({}, {'user_id': 1, 'is_active': 1})
            return [(user['user_id'], user.get('is_active', True)) for user in users]
        except Exception as e:
            logger.error(f"Error getting users from MongoDB: {e}")
            return []
    else:
        # Возвращаем пользователей из локального хранилища
        return [(user_id, data['is_active']) for user_id, data in local_users.items()]

async def set_user_active_status(user_id: int, is_active: bool) -> None:
    """Устанавливает статус активности пользователя"""
    if users_collection:
        try:
            users_collection.update_one(
                {'user_id': user_id},
                {'$set': {'is_active': is_active}},
                upsert=True
            )
            logger.info(f"User {user_id} status updated to {is_active} in MongoDB")
        except Exception as e:
            logger.error(f"Error updating user status in MongoDB: {e}")
    else:
        if user_id in local_users:
            local_users[user_id]['is_active'] = is_active
            logger.info(f"User {user_id} status updated to {is_active} in local storage")

async def get_stat() -> Dict:
    """Получает статистику пользователей"""
    if users_collection:
        try:
            total = users_collection.count_documents({})
            active = users_collection.count_documents({'is_active': True})
            promo_users = users_collection.count_documents({'used_start_promo': True})
            
            return {
                "users_count": total,
                "active_users_count": active,
                "no_active_users_count": total - active,
                "count_users_start_promotion": promo_users
            }
        except Exception as e:
            logger.error(f"Error getting statistics from MongoDB: {e}")
            return {
                "users_count": 0,
                "active_users_count": 0,
                "no_active_users_count": 0,
                "count_users_start_promotion": 0
            }
    else:
        # Считаем статистику из локального хранилища
        total = len(local_users)
        active = sum(1 for user in local_users.values() if user['is_active'])
        promo_users = sum(1 for user in local_users.values() if user['used_start_promo'])
        
        return {
            "users_count": total,
            "active_users_count": active,
            "no_active_users_count": total - active,
            "count_users_start_promotion": promo_users
        } 