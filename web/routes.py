"""
HTML страницы для StellarTracker
"""
from flask import Blueprint, render_template
from flask_login import login_required
from web.config import get_config

routes_bp = Blueprint('routes', __name__)
config = get_config()


@routes_bp.route('/')
@login_required
def index():
    """Главная страница - Dashboard"""
    return render_template('index.html')


@routes_bp.route('/upload')
@login_required
def upload_page():
    """Страница загрузки наблюдений"""
    return render_template('upload.html', csv_limit=config.CSV_CLIENT_PARSE_LIMIT)


@routes_bp.route('/objects')
@login_required
def objects_page():
    """Каталог отслеживаемых объектов"""
    return render_template('objects.html')


@routes_bp.route('/monitoring')
@login_required
def monitoring_page():
    """Страница мониторинга системы"""
    return render_template('monitoring.html')
