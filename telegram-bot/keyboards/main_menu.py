from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_main_menu() -> ReplyKeyboardMarkup:
    """Главное меню с кнопками"""
    keyboard = [
        [
            KeyboardButton(text="📊 Статус"),
            KeyboardButton(text="📈 Статистика")
        ],
        [
            KeyboardButton(text="🚨 Алерты"),
            KeyboardButton(text="💚 Здоровье")
        ],
        [
            KeyboardButton(text="ℹ️ Помощь")
        ]
    ]
    
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Выберите команду..."
    )
