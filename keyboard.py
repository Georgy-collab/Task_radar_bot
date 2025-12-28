"""
Модуль для создания клавиатур бота.
Здесь находятся функции для создания интерактивных кнопок.
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_category_keyboard():
    """
    Создает клавиатуру с кнопками для выбора категории задачи.
    
    Returns:
        InlineKeyboardMarkup с кнопками категорий
    """
    # Создаем кнопки для каждой категории
    buttons = [
        [
            InlineKeyboardButton(text="💾 DataBase", callback_data="category_DataBase"),
            InlineKeyboardButton(text="🎨 Frontend", callback_data="category_Frontend")
        ],
        [
            InlineKeyboardButton(text="⚙️ Backend", callback_data="category_Backend"),
            InlineKeyboardButton(text="💼 Business", callback_data="category_Business")
        ]
    ]
    
    # Создаем клавиатуру из кнопок
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    return keyboard


def get_category_filter_keyboard():
    """
    Создает клавиатуру с кнопками для фильтрации задач по категории.
    
    Returns:
        InlineKeyboardMarkup с кнопками категорий для фильтрации
    """
    # Создаем кнопки для каждой категории с другим префиксом callback_data
    buttons = [
        [
            InlineKeyboardButton(text="💾 DataBase", callback_data="filter_category_DataBase"),
            InlineKeyboardButton(text="🎨 Frontend", callback_data="filter_category_Frontend")
        ],
        [
            InlineKeyboardButton(text="⚙️ Backend", callback_data="filter_category_Backend"),
            InlineKeyboardButton(text="💼 Business", callback_data="filter_category_Business")
        ]
    ]
    
    # Создаем клавиатуру из кнопок
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    
    return keyboard

