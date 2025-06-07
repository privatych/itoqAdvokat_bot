from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from keyboards.admin import create_admin_keyboard
from services.user_service import get_all_users, set_user_active_status, get_stat
from states.admin import AdminState
from logging import getLogger, ERROR
from config import ADMIN_ID

logger = getLogger(__name__)
admin_router = Router()

def is_admin(user_id: int) -> bool:
    """Проверка на администратора"""
    return user_id == ADMIN_ID

@admin_router.message(Command("admin"))
async def cmd_admin(message: Message):
    """Обработчик команды /admin"""
    if not is_admin(message.from_user.id):
        return
        
    await message.answer(
        text="👋 Добро пожаловать в панель администратора\n\n"
             "Выберите нужное действие из меню ниже:",
        reply_markup=await create_admin_keyboard()
    )

@admin_router.callback_query(F.data == "admin_menu")
async def process_admin_menu(callback: CallbackQuery, state: FSMContext):
    """Обработчик возврата в главное меню админки"""
    if not is_admin(callback.from_user.id):
        await callback.answer("У вас нет прав администратора", show_alert=True)
        return

    await state.clear()
    await callback.answer()
    
    try:
        await callback.message.edit_text(
            text="👋 Добро пожаловать в панель администратора\n\n"
                 "Выберите нужное действие из меню ниже:",
            reply_markup=await create_admin_keyboard()
        )
    except Exception as e:
        logger.error(f"Ошибка при обновлении меню админки: {e}")
        await callback.message.answer(
            text="👋 Добро пожаловать в панель администратора\n\n"
                 "Выберите нужное действие из меню ниже:",
            reply_markup=await create_admin_keyboard()
        )

@admin_router.callback_query(F.data == "get_stat")
async def process_get_stat(callback: CallbackQuery):
    """Обработчик получения статистики"""
    if not is_admin(callback.from_user.id):
        await callback.answer("У вас нет прав администратора", show_alert=True)
        return

    await callback.answer()
    
    try:
        stat_data = await get_stat()
        
        message_text = (
            "📊 <b>Статистика бота:</b>\n\n"
            f"👥 Всего пользователей: <b>{stat_data['users_count']}</b>\n"
            f"✅ Активных: <b>{stat_data['active_users_count']}</b>\n"
            f"❌ Неактивных: <b>{stat_data['no_active_users_count']}</b>\n"
            f"🎁 Использовали промокод: <b>{stat_data['count_users_start_promotion']}</b>"
        )

        await callback.message.edit_text(
            text=message_text,
            parse_mode="HTML",
            reply_markup=await create_admin_keyboard(show_back=True)
        )
    except Exception as e:
        logger.error(f"Ошибка при получении статистики: {e}")
        await callback.message.answer(
            "❌ Произошла ошибка при получении статистики. Попробуйте позже.",
            reply_markup=await create_admin_keyboard(show_back=True)
        )

@admin_router.callback_query(F.data == "send_broadcast")
async def process_broadcast_start(callback: CallbackQuery, state: FSMContext):
    """Начало процесса рассылки"""
    if not is_admin(callback.from_user.id):
        await callback.answer("У вас нет прав администратора", show_alert=True)
        return

    await callback.answer()
    await state.set_state(AdminState.broadcast_message)
    
    msg = await callback.message.edit_text(
        text="📝 Отправьте сообщение для рассылки.\n"
             "Поддерживаются текст, фото и видео.\n\n"
             "<i>Для отмены нажмите кнопку ниже</i>",
        parse_mode="HTML",
        reply_markup=await create_admin_keyboard(show_back=True)
    )
    
    await state.update_data(last_message_id=msg.message_id)

@admin_router.message(AdminState.broadcast_message)
async def process_broadcast_message(message: Message, state: FSMContext):
    """Обработка сообщения для рассылки"""
    if not is_admin(message.from_user.id):
        return

    state_data = await state.get_data()
    last_message_id = state_data.get("last_message_id")

    if last_message_id:
        try:
            await message.bot.delete_message(message.chat.id, last_message_id)
        except Exception as e:
            logger.error(f"Ошибка при удалении сообщения: {e}")

    # Получаем данные сообщения
    text_data = message.text or message.caption or ""
    photo = message.photo[-1] if message.photo else None
    video = message.video

    await state.update_data(text_data=text_data, photo=photo, video=video)
    
    # Формируем превью сообщения
    try:
        if photo:
            await message.answer_photo(
                photo=photo.file_id,
                caption=f"📱 Предпросмотр рассылки:\n\n{text_data}",
                parse_mode="HTML",
                reply_markup=await create_admin_keyboard(show_confirm=True)
            )
        elif video:
            await message.answer_video(
                video=video.file_id,
                caption=f"📱 Предпросмотр рассылки:\n\n{text_data}",
                parse_mode="HTML",
                reply_markup=await create_admin_keyboard(show_confirm=True)
            )
        else:
            await message.answer(
                text=f"📱 Предпросмотр рассылки:\n\n{text_data}",
                parse_mode="HTML",
                reply_markup=await create_admin_keyboard(show_confirm=True)
            )
        
        await state.set_state(AdminState.confirm_message)
    except Exception as e:
        logger.error(f"Ошибка при создании предпросмотра: {e}")
        await message.answer(
            "❌ Произошла ошибка при обработке сообщения. Попробуйте еще раз.",
            reply_markup=await create_admin_keyboard(show_back=True)
        )

@admin_router.callback_query(F.data == "broadcast_confirm", AdminState.confirm_message)
async def process_broadcast_confirm(callback: CallbackQuery, state: FSMContext):
    """Подтверждение и выполнение рассылки"""
    if not is_admin(callback.from_user.id):
        await callback.answer("У вас нет прав администратора", show_alert=True)
        return

    await callback.answer()
    
    try:
        message_data = await state.get_data()
        text_data = message_data.get("text_data", "")
        photo = message_data.get("photo")
        video = message_data.get("video")

        users = await get_all_users()
        if not users:
            await callback.message.edit_text(
                "❌ Нет пользователей для рассылки",
                reply_markup=await create_admin_keyboard(show_back=True)
            )
            await state.clear()
            return

        total_users = len(users)
        success_count = 0
        failed_count = 0

        # Сообщение о прогрессе
        progress_msg = await callback.message.edit_text(
            "🔄 Начинаем рассылку...\n"
            f"Всего пользователей: {total_users}"
        )

        for i, user in enumerate(users, 1):
            try:
                if photo:
                    await callback.bot.send_photo(
                        chat_id=user[0],
                        photo=photo.file_id,
                        caption=text_data,
                        parse_mode="HTML"
                    )
                elif video:
                    await callback.bot.send_video(
                        chat_id=user[0],
                        video=video.file_id,
                        caption=text_data,
                        parse_mode="HTML"
                    )
                else:
                    await callback.bot.send_message(
                        chat_id=user[0],
                        text=text_data,
                        parse_mode="HTML"
                    )
                success_count += 1
                await set_user_active_status(user[0], True)
            except Exception as e:
                logger.error(f"Ошибка при отправке пользователю {user[0]}: {e}")
                failed_count += 1
                await set_user_active_status(user[0], False)

            # Обновляем прогресс каждые 10 пользователей
            if i % 10 == 0 or i == total_users:
                try:
                    await progress_msg.edit_text(
                        f"🔄 Рассылка в процессе...\n"
                        f"Прогресс: {i}/{total_users} ({int(i/total_users*100)}%)\n"
                        f"✅ Успешно: {success_count}\n"
                        f"❌ Неудачно: {failed_count}"
                    )
                except Exception as e:
                    logger.error(f"Ошибка при обновлении прогресса: {e}")

        # Итоговое сообщение
        await progress_msg.edit_text(
            f"✅ Рассылка завершена!\n\n"
            f"📊 Результаты:\n"
            f"👥 Всего пользователей: {total_users}\n"
            f"✅ Успешно отправлено: {success_count}\n"
            f"❌ Не удалось отправить: {failed_count}",
            reply_markup=await create_admin_keyboard(show_back=True)
        )

    except Exception as e:
        logger.error(f"Критическая ошибка при рассылке: {e}")
        await callback.message.edit_text(
            "❌ Произошла критическая ошибка при рассылке.\n"
            "Пожалуйста, попробуйте позже.",
            reply_markup=await create_admin_keyboard(show_back=True)
        )
    finally:
        await state.clear() 