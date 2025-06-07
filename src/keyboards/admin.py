from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from typing import List
from aiogram.utils.keyboard import InlineKeyboardBuilder

async def create_inline_keyboard(buttons: List[str], callbacks: List[str]) -> InlineKeyboardMarkup:
    """Создает inline клавиатуру из списка кнопок и их callback_data"""
    keyboard = []
    for button, callback in zip(buttons, callbacks):
        keyboard.append([InlineKeyboardButton(text=button, callback_data=callback)])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_admin_keyboard() -> ReplyKeyboardMarkup:
    """Создает клавиатуру админ-панели"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📢 Рассылка"),
                KeyboardButton(text="📊 Статистика")
            ]
        ],
        resize_keyboard=True
    )
    return keyboard

def get_broadcast_keyboard() -> ReplyKeyboardMarkup:
    """Создает клавиатуру для рассылки"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="❌ Отменить")
            ]
        ],
        resize_keyboard=True
    )
    return keyboard

async def create_admin_keyboard(show_back: bool = False, show_confirm: bool = False) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для админ-панели
    
    Args:
        show_back (bool): Показывать ли кнопку "Назад"
        show_confirm (bool): Показывать ли кнопки подтверждения
    """
    builder = InlineKeyboardBuilder()
    
    if show_confirm:
        builder.row(
            InlineKeyboardButton(text="✅ Подтвердить", callback_data="broadcast_confirm"),
            InlineKeyboardButton(text="❌ Отменить", callback_data="admin_menu")
        )
        return builder.as_markup()
    
    if show_back:
        builder.row(InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data="admin_menu"
        ))
        return builder.as_markup()
    
    # Основное меню
    builder.row(
        InlineKeyboardButton(text="📊 Статистика", callback_data="get_stat"),
        InlineKeyboardButton(text="📨 Рассылка", callback_data="send_broadcast")
    )
    
    return builder.as_markup() 