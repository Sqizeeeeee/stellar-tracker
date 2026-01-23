from aiohttp import web
from aiogram import Bot
from typing import Dict, Any
import json

from config import settings
from services.alertmanager import parse_alertmanager_webhook, format_alert_notification


class WebhookHandler:
    """Handler для webhook от Alertmanager"""
    
    def __init__(self, bot: Bot):
        self.bot = bot
        self.app = web.Application()
        self.setup_routes()
    
    def setup_routes(self):
        """Настройка маршрутов"""
        self.app.router.add_post(settings.webhook_path, self.handle_alert)
        self.app.router.add_get("/health", self.health_check)
    
    async def health_check(self, request: web.Request) -> web.Response:
        """Health check endpoint"""
        return web.json_response({"status": "ok"})
    
    async def handle_alert(self, request: web.Request) -> web.Response:
        """Обработка алерта от Alertmanager"""
        try:
            # Получаем payload
            payload = await request.json()
            
            # Парсим
            alert_data = parse_alertmanager_webhook(payload)
            
            # Форматируем сообщения
            messages = format_alert_notification(alert_data)
            
            if messages:
                # Отправляем всем разрешенным пользователям
                for user_id in settings.allowed_ids:
                    for msg in messages:
                        try:
                            await self.bot.send_message(
                                chat_id=user_id,
                                text=msg,
                                parse_mode="HTML"
                            )
                        except Exception as e:
                            print(f"Error sending alert to {user_id}: {e}")
            
            return web.json_response({"status": "ok"})
            
        except Exception as e:
            print(f"Error handling webhook: {e}")
            return web.json_response(
                {"status": "error", "message": str(e)},
                status=500
            )
    
    async def start(self):
        """Запуск webhook сервера"""
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(
            runner,
            settings.webhook_host,
            settings.webhook_port
        )
        await site.start()
        print(f"🌐 Webhook server started on {settings.webhook_host}:{settings.webhook_port}")
