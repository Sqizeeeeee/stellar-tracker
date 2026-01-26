"""
Flask веб-интерфейс для StellarTracker
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
import grpc
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import astro_pb2
import astro_pb2_grpc
from database import User, AstroObject, Observation, ProcessingHistory
from config import get_config
from grpc_client import grpc_client
from auth import auth_bp
from routes import routes_bp
from api import api_bp
from middleware import register_middleware
import logging

# Загружаем конфигурацию
config = get_config()

app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY

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

LOGS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
os.makedirs(LOGS_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOGS_DIR, "app.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger("web")

logger.info("web app.py loaded")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=config.DEBUG)
