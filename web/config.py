"""
Configuration for StellarTracker Web Interface
"""
import os


class Config:
    """Base configuration"""

    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'stellartracker-secret-key-change-in-production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'production')
    DEBUG = FLASK_ENV == 'development'

    # gRPC Services
    ORCHESTRATOR_HOST = os.getenv('ORCHESTRATOR_HOST', 'localhost')
    ORCHESTRATOR_PORT = os.getenv('ORCHESTRATOR_PORT', '50051')
    ORBIT_SERVICE_HOST = os.getenv('ORBIT_SERVICE_HOST', 'localhost')
    ORBIT_SERVICE_PORT = os.getenv('ORBIT_SERVICE_PORT', '50052')
    COLLISION_SERVICE_HOST = os.getenv('COLLISION_SERVICE_HOST', 'localhost')
    COLLISION_SERVICE_PORT = os.getenv('COLLISION_SERVICE_PORT', '50053')

    # SocketIO
    SOCKETIO_CORS_ALLOWED_ORIGINS = "*"
    SOCKETIO_ASYNC_MODE = 'eventlet'
    SOCKETIO_LOGGER = True
    SOCKETIO_ENGINEIO_LOGGER = False
    SOCKETIO_PING_TIMEOUT = 60
    SOCKETIO_PING_INTERVAL = 25

    # Flask-Login
    LOGIN_VIEW = 'auth.login'
    LOGIN_MESSAGE = 'Please log in to access this page.'

    # CSV Upload
    CSV_CLIENT_PARSE_LIMIT = int(os.getenv('CSV_CLIENT_PARSE_LIMIT', '15'))

    @property
    def orchestrator_address(self):
        return f'{self.ORCHESTRATOR_HOST}:{self.ORCHESTRATOR_PORT}'

    @property
    def orbit_service_address(self):
        return f'{self.ORBIT_SERVICE_HOST}:{self.ORBIT_SERVICE_PORT}'

    @property
    def collision_service_address(self):
        return f'{self.COLLISION_SERVICE_HOST}:{self.COLLISION_SERVICE_PORT}'


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    FLASK_ENV = 'development'


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    FLASK_ENV = 'production'


# Выбор конфига по переменной окружения
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': ProductionConfig
}


def get_config():
    """Get configuration based on FLASK_ENV"""
    env = os.getenv('FLASK_ENV', 'production')
    return config.get(env, config['default'])()
