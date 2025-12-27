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
from web.database_simple import User
from web.config import get_config
from web.grpc_client import grpc_client
from web.auth import auth_bp

# Загружаем конфигурацию
config = get_config()

# Prometheus метрики
REQUEST_COUNT = Counter('web_requests_total', 'Total web requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('web_request_duration_seconds', 'Request latency', ['endpoint'])

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

# Регистрируем Blueprint для аутентификации
app.register_blueprint(auth_bp)

# gRPC каналы
orchestrator_channel = grpc.insecure_channel(config.orchestrator_address)
orbit_channel = grpc.insecure_channel(config.orbit_service_address)
collision_channel = grpc.insecure_channel(config.collision_service_address)

orchestrator_stub = astro_pb2_grpc.OrchestratorServiceStub(orchestrator_channel)
orbit_stub = astro_pb2_grpc.OrbitServiceStub(orbit_channel)
collision_stub = astro_pb2_grpc.CollisionServiceStub(collision_channel)


# Protected routes
@app.route('/')
@login_required
def index():
    """Главная страница - Dashboard"""
    return render_template('index.html')


@app.route('/upload')
@login_required
def upload_page():
    """Страница загрузки наблюдений"""
    return render_template('upload.html')


@app.route('/objects')
@login_required
def objects_page():
    """Каталог отслеживаемых объектов"""
    return render_template('objects.html')


@app.route('/monitoring')
@login_required
def monitoring_page():
    """Страница мониторинга системы"""
    return render_template('monitoring.html')


# REST API endpoints
@app.route('/api/process', methods=['POST'])
@login_required
def api_process_observations():
    """Обработка наблюдений через Orchestrator"""
    try:
        data = request.json
        
        # Конвертируем в gRPC формат
        observations = [
            astro_pb2.Observation(
                obs_time=obs['obs_time'],
                ra_deg=float(obs['ra_deg']),
                dec_deg=float(obs['dec_deg']),
                station=obs.get('station', '500'),
                catalog=obs.get('catalog', 'Gaia2')
            )
            for obs in data['observations']
        ]
        
        request_msg = astro_pb2.ObservationsRequest(
            request_id=data.get('request_id', f'web-{datetime.now().timestamp()}'),
            object_name=data['object_name'],
            observations=observations
        )
        
        # Отправляем в Orchestrator
        response = grpc_client.orchestrator_stub.Process(request_msg, timeout=30.0)
        
        # Отправляем real-time обновление через WebSocket
        if response.success:
            socketio.emit('new_object', {
                'object_name': data['object_name'],
                'risk_level': response.risk.risk_level if response.risk else 'unknown',
                'moid': response.risk.moid_earth_au if response.risk else None,
                'timestamp': datetime.now().isoformat()
            })
        
        return jsonify({
            'success': response.success,
            'error': response.error,
            'orbit': {
                'a_au': response.orbit.a_au,
                'e': response.orbit.e,
                'i_deg': response.orbit.i_deg,
                'omega_deg': response.orbit.omega_deg,
                'big_omega_deg': response.orbit.big_mega_deg,
                'M_deg': response.orbit.M_deg,
                'epoch': response.orbit.epoch
            } if response.success and response.orbit else None,
            'risk': {
                'risk_level': response.risk.risk_level,
                'moid_earth_au': response.risk.moid_earth_au,
                'potential_impact': response.risk.potential_impact,
                'closest_approach': response.risk.closest_approach
            } if response.success and response.risk else None
        })
        
    except grpc.RpcError as e:
        return jsonify({'success': False, 'error': f'gRPC Error: {e.code()}'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/orbit/calculate', methods=['POST'])
@login_required
def api_calculate_orbit():
    """Расчет орбиты по наблюдениям"""
    try:
        data = request.json
        observations = [
            astro_pb2.Observation(
                obs_time=obs['obs_time'],
                ra_deg=float(obs['ra_deg']),
                dec_deg=float(obs['dec_deg']),
                station=obs.get('station', '500'),
                catalog=obs.get('catalog', 'Gaia2')
            )
            for obs in data['observations']
        ]
        
        request_msg = astro_pb2.ObservationsRequest(
            request_id=data.get('request_id', f'orbit-{datetime.now().timestamp()}'),
            object_name=data['object_name'],
            observations=observations
        )
        
        response = grpc_client.orbit_stub.Calculate(request_msg, timeout=15.0)
        
        return jsonify({
            'success': response.success,
            'error': response.error,
            'orbit': {
                'a_au': response.orbit.a_au,
                'e': response.orbit.e,
                'i_deg': response.orbit.i_deg,
                'omega_deg': response.orbit.omega_deg,
                'big_omega_deg': response.orbit.big_mega_deg,
                'M_deg': response.orbit.M_deg,
                'epoch': response.orbit.epoch
            } if response.success and response.orbit else None
        })
        
    except grpc.RpcError as e:
        return jsonify({'success': False, 'error': f'gRPC Error: {e.code()}'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/collision/assess', methods=['POST'])
@login_required
def api_assess_collision():
    """Оценка риска столкновения"""
    try:
        data = request.json
        orbit = astro_pb2.OrbitElements(
            a_au=float(data['a_au']),
            e=float(data['e']),
            i_deg=float(data['i_deg']),
            omega_deg=float(data['omega_deg']),
            big_mega_deg=float(data['big_omega_deg']),
            M_deg=float(data['M_deg']),
            epoch=data['epoch']
        )
        
        response = grpc_client.collision_stub.AssessRisk(orbit, timeout=10.0)
        
        return jsonify({
            'success': response.success,
            'error': response.error,
            'risk': {
                'risk_level': response.risk.risk_level,
                'moid_earth_au': response.risk.moid_earth_au,
                'potential_impact': response.risk.potential_impact,
                'closest_approach': response.risk.closest_approach
            } if response.success and response.risk else None
        })
        
    except grpc.RpcError as e:
        return jsonify({'success': False, 'error': f'gRPC Error: {e.code()}'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@app.route('/api/health')
def api_health():
    """Проверка здоровья сервисов"""
    health = {
        'orchestrator': grpc_client.check_health('orchestrator'),
        'orbit_service': grpc_client.check_health('orbit_service'),
        'collision_service': grpc_client.check_health('collision_service')
    }
    return jsonify(health)


# Prometheus endpoint
@app.route('/metrics')
def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

# Middleware для подсчета метрик
@app.before_request
def before_request():
    request.start_time = datetime.now()

@app.after_request
def after_request(response):
    if hasattr(request, 'start_time'):
        latency = (datetime.now() - request.start_time).total_seconds()
        REQUEST_LATENCY.labels(endpoint=request.endpoint or 'unknown').observe(latency)
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.endpoint or 'unknown',
            status=response.status_code
        ).inc()
    return response


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
