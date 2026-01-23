from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # Telegram
    telegram_bot_token: str
    allowed_user_ids: str
    
    # Monitoring (defaults для Docker)
    prometheus_url: str = "http://prometheus:9090"
    alertmanager_url: str = "http://alertmanager:9093"
    
    # Webhook
    webhook_host: str = "0.0.0.0"
    webhook_port: int = 8080
    webhook_path: str = "/webhook/alerts"
    
    class Config:
        # В Docker используем переменные окружения, локально - .env файл
        env_file = os.path.join(os.path.dirname(__file__), "..", ".env")
        case_sensitive = False
        extra = "ignore"
    
    @property
    def allowed_ids(self) -> List[int]:
        """Парсим ALLOWED_USER_IDS в список int"""
        return [int(id.strip()) for id in self.allowed_user_ids.split(",")]


settings = Settings()
