"""
HTML страницы для StellarTracker
"""
from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from config import get_config
from database import AstroObject, serialize_mongo_object, ProcessingHistory, observations_collection

routes_bp = Blueprint('routes', __name__)
config = get_config()


@routes_bp.route('/')
@login_required
def index():
    """Главная страница - Dashboard"""
    # Получаем статистику
    object_stats = AstroObject.get_stats()
    processing_stats = ProcessingHistory.get_stats()

    # Объекты с высоким риском
    high_risk_objects = AstroObject.get_high_risk(limit=5)

    # Недавние объекты пользователя
    user_recent = AstroObject.get_by_user(current_user.email, limit=10)

    # Популярные объекты
    popular_objects = AstroObject.get_popular(limit=10)

    # Общая статистика наблюдений
    total_observations = observations_collection.count_documents({})

    print(f"📊 Dashboard stats: objects={object_stats}, processing={processing_stats}")

    return render_template('index.html',
                           object_stats=object_stats,
                           processing_stats=processing_stats,
                           high_risk_objects=high_risk_objects,
                           user_recent=user_recent,
                           popular_objects=popular_objects,
                           total_observations=total_observations)


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


@routes_bp.route('/api/objects/recent')
@login_required
def get_recent_objects():
    """Получить последние объекты (для polling)"""
    limit = int(request.args.get('limit', 5))
    objects = AstroObject.find_all(limit=limit)
    return jsonify({
        'success': True,
        'objects': [serialize_mongo_object(obj) for obj in objects]
    })


@routes_bp.route('/api/objects/stats')
@login_required
def get_objects_stats():
    """Получить статистику по объектам (для polling)"""
    stats = AstroObject.get_stats()
    return jsonify({
        'success': True,
        'stats': stats
    })
