"""
Flask веб-интерфейс для StellarTracker
"""
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
try:
    from flask_socketio import SocketIO, emit
except ImportError:
    print("⚠️  flask-socketio не установлен. pip install flask-socketio")
    raise

from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import grpc
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from web.proto import astro_pb2, astro_pb2_grpc
from web.database import User, AstroObject, Observation, ProcessingHistory
from web.config import get_config
from web.grpc_client import grpc_client
from web.auth import auth_bp
from web.routes import routes_bp
from web.api import api_bp
from web.middleware import register_middleware

# Загружаем конфигурацию
config = get_config()

app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY
socketio = SocketIO(
    app, 
    cors_allowed_origins=config.SOCKETIO_CORS_ALLOWED_ORIGINS,
    async_mode=config.SOCKETIO_ASYNC_MODE,
    logger=config.SOCKETIO_LOGGER,
    engineio_logger=config.SOCKETIO_ENGINEIO_LOGGER,
    ping_timeout=config.SOCKETIO_PING_TIMEOUT,
    ping_interval=config.SOCKETIO_PING_INTERVAL
)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = config.LOGIN_VIEW
login_manager.login_message = config.LOGIN_MESSAGE

@login_manager.user_loader
def load_user(user_id):
    return User.find_by_id(user_id)

# Регистрируем Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(routes_bp)
app.register_blueprint(api_bp)

# Регистрируем middleware
register_middleware(app)

# Metrics endpoint для Prometheus (корневой путь для совместимости)
@app.route('/metrics')
def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

# WebSocket события
@socketio.on('connect')
def handle_connect():
    """Клиент подключился"""
    if current_user.is_authenticated:
        emit('status', {'message': f'Connected as {current_user.username}'})

@socketio.on('disconnect')
def handle_disconnect():
    """Клиент отключился"""
    print('Client disconnected')


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5001, debug=config.DEBUG)
