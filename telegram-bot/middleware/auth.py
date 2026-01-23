from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message
from config import settings


class AuthMiddleware(BaseMiddleware):
    """Middleware для проверки авторизации пользователя"""
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        user_id = event.from_user.id if event.from_user else None
        
        if user_id not in settings.allowed_ids:
            await event.answer(
                "🚫 Access denied.\n"
                "You are not authorized to use this bot."
            )
            return
        
        # Пользователь авторизован, продолжаем обработку
        return await handler(event, data)
