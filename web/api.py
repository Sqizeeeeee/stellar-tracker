"""
REST API endpoints для StellarTracker
"""
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, Counter, Histogram
import grpc
import csv
import io
import sys
from datetime import datetime

import astro_pb2
from database import AstroObject, Observation, ProcessingHistory
from grpc_client import grpc_client

# Prometheus метрики для пользовательских событий
USER_EVENTS = Counter(
    'user_events_total', 
    'User frontend events', 
    ['event_name', 'user']
)

CSV_PARSE_OPERATIONS = Counter(
    'csv_parse_operations_total', 
    'CSV parse operations', 
    ['method', 'status']
)

CSV_PARSE_DURATION = Histogram(
    'csv_parse_duration_seconds', 
    'CSV parse duration', 
    ['method'],
    buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10)
)

PROCESSING_OPERATIONS = Counter(
    'processing_operations_total', 
    'Processing operations', 
    ['status']
)

PROCESSING_DURATION = Histogram(
    'processing_duration_seconds', 
    'Processing duration',
    buckets=(0.1, 0.5, 1, 2, 5, 10, 30, 60)
)

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/metrics/event', methods=['POST'])
def log_metric_event():
    """Логирование событий с фронтенда для аналитики"""
    try:
        data = request.json
        event_name = data.get('event')
        
        user_email = 'anonymous'
        if current_user and current_user.is_authenticated:
            user_email = current_user.email
        
        if not event_name:
            return jsonify({'success': False, 'error': 'event name required'}), 400
        
        USER_EVENTS.labels(event_name=event_name, user=user_email).inc()
        
        if event_name == 'csv_parsed_client':
            CSV_PARSE_OPERATIONS.labels(method='client', status='success').inc()
            parse_time = data.get('parseTime', 0) / 1000.0
            if parse_time > 0:
                CSV_PARSE_DURATION.labels(method='client').observe(parse_time)
        
        elif event_name == 'csv_parsed_server':
            status = 'error' if data.get('hasErrors') else 'success'
            CSV_PARSE_OPERATIONS.labels(method='server', status=status).inc()
            parse_time = data.get('parseTime', 0) / 1000.0
            if parse_time > 0:
                CSV_PARSE_DURATION.labels(method='server').observe(parse_time)
        
        elif event_name == 'csv_parse_error':
            CSV_PARSE_OPERATIONS.labels(method='unknown', status='error').inc()
        
        elif event_name == 'processing_success':
            PROCESSING_OPERATIONS.labels(status='success').inc()
            proc_time = data.get('processingTime', 0) / 1000.0
            if proc_time > 0:
                PROCESSING_DURATION.observe(proc_time)
        
        elif event_name in ['processing_failed', 'processing_error']:
            PROCESSING_OPERATIONS.labels(status='failed').inc()
        
        return jsonify({'success': True}), 200
        
    except Exception as e:
        print(f"❌ Error logging metric event: {e}", file=sys.stderr, flush=True)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/process', methods=['POST'])
@login_required
def process_observations():
    """Обработка наблюдений через Orchestrатор"""
    print("🔵 /api/process called", file=sys.stderr, flush=True)
    print(f"   Content-Type: {request.content_type}", file=sys.stderr, flush=True)
    print(f"   Content-Length: {request.content_length}", file=sys.stderr, flush=True)
    start_time = datetime.now()
    
    try:
        print("🔵 Getting request.json...", file=sys.stderr, flush=True)
        data = request.json
        print(f"📥 Received data keys: {list(data.keys()) if data else 'None'}", file=sys.stderr, flush=True)
        request_id = data.get('request_id', f'web-{datetime.now().timestamp()}')
        
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
            request_id=request_id,
            object_name=data['object_name'],
            observations=observations
        )
        response = grpc_client.call_orchestrator_process(request_msg)
        
        # Проверяем что ответ содержит нужные поля
        has_orbit = 'orbit' in [f.name for f in response.DESCRIPTOR.fields]
        has_risk = 'risk' in [f.name for f in response.DESCRIPTOR.fields]
        
        print(f"✅ Orchestrator response: success={response.success}, error={response.error}", file=sys.stderr, flush=True)
        print(f"   has_orbit={has_orbit}, has_risk={has_risk}", file=sys.stderr, flush=True)
        
        # Вычисляем время обработки
        processing_time = (datetime.now() - start_time).total_seconds()
        
        if not response.success:
            return jsonify({
                'success': False,
                'error': response.error or 'Processing failed'
            }), 400
        
        if not has_orbit:
            return jsonify({
                'success': False,
                'error': 'Orchestrator returned wrong response type (no orbit data)'
            }), 500
        
        if response.success and has_orbit and has_risk:
            print("🔵 Entering save block...", file=sys.stderr, flush=True)
            
            # Сохраняем объект в БД
            user_email = current_user.email if current_user.is_authenticated else 'anonymous'
            
            print(f"🔵 Saving object: {data['object_name']}, user: {user_email}", file=sys.stderr, flush=True)
            print(f"🔵 Orbit data: {response.orbit}", file=sys.stderr, flush=True)
            print(f"🔵 Risk data: {response.risk}", file=sys.stderr, flush=True)
            
            try:
                result = AstroObject.create(
                    object_name=data['object_name'],
                    orbit_data={
                        'a_au': response.orbit.a_au,
                        'e': response.orbit.e,
                        'i_deg': response.orbit.i_deg,
                        'omega_deg': response.orbit.omega_deg,
                        'big_mega_deg': response.orbit.big_mega_deg,
                        'm_deg': response.orbit.m_deg,
                        'epoch': response.orbit.epoch
                    },
                    risk_data={
                        'risk_level': response.risk.risk_level,
                        'moid_earth_au': response.risk.moid_earth_au,
                        'potential_impact': response.risk.potential_impact
                    },
                    created_by_email=user_email
                )
                print(f"✅ Object create result: {result is not None}", file=sys.stderr, flush=True)
            except Exception as save_error:
                print(f"❌ Error in AstroObject.create: {save_error}", file=sys.stderr, flush=True)
                import traceback
                traceback.print_exc(file=sys.stderr)
            
            # Сохраняем наблюдения в БД
            print(f"🔵 Saving {len(data['observations'])} observations...", file=sys.stderr, flush=True)
            for obs in data['observations']:
                try:
                    Observation.create(
                        object_name=data['object_name'],
                        obs_time=obs['obs_time'],
                        ra_deg=float(obs['ra_deg']),
                        dec_deg=float(obs['dec_deg']),
                        station=obs.get('station', '500'),
                        catalog=obs.get('catalog', 'Gaia2'),
                        created_by_email=user_email
                    )
                except Exception as obs_error:
                    print(f"❌ Error saving observation: {obs_error}", file=sys.stderr, flush=True)
            
            # Сохраняем историю успешной обработки
            ProcessingHistory.create(
                request_id=request_id,
                object_name=data['object_name'],
                status='success',
                processing_time=processing_time,
                created_by_email=user_email
            )
        else:
            # Сохраняем историю ошибки
            user_email = current_user.email if current_user.is_authenticated else 'anonymous'
            ProcessingHistory.create(
                request_id=request_id,
                object_name=data['object_name'],
                status='error',
                error_message=response.error,
                processing_time=processing_time,
                created_by_email=user_email
            )
        
        return jsonify({
            'success': response.success,
            'error': response.error,
            'orbit': {
                'a_au': response.orbit.a_au,
                'e': response.orbit.e,
                'i_deg': response.orbit.i_deg,
                'omega_deg': response.orbit.omega_deg,
                'big_mega_deg': response.orbit.big_mega_deg,
                'm_deg': response.orbit.m_deg,
                'epoch': response.orbit.epoch
            } if has_orbit else None,
            'risk': {
                'risk_level': response.risk.risk_level,
                'moid_earth_au': response.risk.moid_earth_au,
                'potential_impact': response.risk.potential_impact
            } if has_risk else None
        })
        
    except grpc.RpcError as e:
        # Сохраняем ошибку gRPC
        user_email = current_user.email if current_user.is_authenticated else 'anonymous'
        ProcessingHistory.create(
            request_id=request_id,
            object_name=data.get('object_name', 'unknown'),
            status='error',
            error_message=f'gRPC Error: {e.code()}',
            processing_time=(datetime.now() - start_time).total_seconds(),
            created_by_email=user_email
        )
        return jsonify({'success': False, 'error': f'gRPC Error: {e.code()}'}), 500
    except Exception as e:
        error_msg = f"❌ Error in /api/process: {type(e).__name__}: {str(e)}"
        print(error_msg, file=sys.stderr, flush=True)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.stderr.flush()
        return jsonify({'success': False, 'error': str(e)}), 400


@api_bp.route('/orbit/calculate', methods=['POST'])
@login_required
def calculate_orbit():
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
                'big_mega_deg': response.orbit.big_mega_deg,
                'm_deg': response.orbit.m_deg,
                'epoch': response.orbit.epoch
            } if response.success and response.orbit else None
        })
        
    except grpc.RpcError as e:
        return jsonify({'success': False, 'error': f'gRPC Error: {e.code()}'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@api_bp.route('/collision/assess', methods=['POST'])
@login_required
def assess_collision():
    """Оценка риска столкновения"""
    try:
        data = request.json
        orbit = astro_pb2.OrbitElements(
            a_au=float(data['a_au']),
            e=float(data['e']),
            i_deg=float(data['i_deg']),
            omega_deg=float(data['omega_deg']),
            big_mega_deg=float(data['big_mega_deg']),
            m_deg=float(data['m_deg']),
            epoch=data['epoch']
        )
        
        response = grpc_client.collision_stub.AssessRisk(orbit, timeout=10.0)
        
        return jsonify({
            'success': response.success,
            'error': response.error,
            'risk': {
                'risk_level': response.risk.risk_level,
                'moid_earth_au': response.risk.moid_earth_au,
                'potential_impact': response.risk.potential_impact
            } if response.success and response.risk else None
        })
        
    except grpc.RpcError as e:
        return jsonify({'success': False, 'error': f'gRPC Error: {e.code()}'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400


@api_bp.route('/health')
def health():
    """Проверка здоровья сервисов"""
    health_status = {
        'orchestrator': grpc_client.check_health('orchestrator'),
        'orbit_service': grpc_client.check_health('orbit_service'),
        'collision_service': grpc_client.check_health('collision_service')
    }
    return jsonify(health_status)


@api_bp.route('/metrics')
def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}


@api_bp.route('/parse-csv', methods=['POST'])
@login_required
def parse_csv():
    """Парсинг большого CSV файла на сервере"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if not file.filename.endswith('.csv'):
            return jsonify({'success': False, 'error': 'File must be CSV'}), 400
        
        # Читаем файл
        stream = io.StringIO(file.stream.read().decode('UTF8'), newline=None)
        csv_reader = csv.DictReader(stream)
        
        observations = []
        errors = []
        
        for row_num, row in enumerate(csv_reader, start=2):  # start=2 т.к. строка 1 - header
            try:
                obs = {
                    'obs_time': row['obs_time'].strip(),
                    'ra_deg': float(row['ra_deg']),
                    'dec_deg': float(row['dec_deg']),
                    'station': row.get('station', '500').strip(),
                    'catalog': row.get('catalog', 'Gaia2').strip()
                }
                
                # Валидация
                if obs['ra_deg'] < 0 or obs['ra_deg'] > 360:
                    errors.append(f"Row {row_num}: RA must be 0-360")
                    continue
                
                if obs['dec_deg'] < -90 or obs['dec_deg'] > 90:
                    errors.append(f"Row {row_num}: Dec must be -90 to 90")
                    continue
                
                observations.append(obs)
                
            except KeyError as e:
                errors.append(f"Row {row_num}: Missing column {e}")
            except ValueError:
                errors.append(f"Row {row_num}: Invalid number format")
        
        if errors and len(observations) == 0:
            return jsonify({
                'success': False,
                'error': f'Failed to parse CSV. Errors: {"; ".join(errors[:5])}'
            }), 400
        
        return jsonify({
            'success': True,
            'observations': observations,
            'count': len(observations),
            'errors': errors if errors else None
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error parsing CSV: {str(e)}'}), 500
