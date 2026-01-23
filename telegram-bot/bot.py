import asyncio
import logging
from aiogram import Bot, Dispatcher

from config import settings
from middleware.auth import AuthMiddleware
from handlers import commands
from handlers.webhook import WebhookHandler

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    # Инициализация бота и диспетчера
    bot = Bot(token=settings.telegram_bot_token)
    dp = Dispatcher()
    
    # Подключаем middleware авторизации
    dp.message.middleware(AuthMiddleware())
    
    # Регистрируем handlers
    dp.include_router(commands.router)
    
    # Запускаем webhook сервер для алертов
    webhook_handler = WebhookHandler(bot)
    await webhook_handler.start()
    
    logger.info("🤖 Bot started!")
    logger.info(f"📋 Allowed user IDs: {settings.allowed_ids}")
    logger.info(f"🌐 Webhook listening on {settings.webhook_host}:{settings.webhook_port}{settings.webhook_path}")
    
    # Запускаем polling
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
