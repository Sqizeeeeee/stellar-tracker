"""
Middleware для StellarTracker
"""
from flask import request
from prometheus_client import Counter, Histogram
from datetime import datetime

# Prometheus метрики
REQUEST_COUNT = Counter('web_requests_total', 'Total web requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('web_request_duration_seconds', 'Request latency', ['endpoint'])


def register_middleware(app):
    """Регистрация middleware для приложения"""
    
    @app.before_request
    def before_request():
        """Сохраняем время начала запроса"""
        request.start_time = datetime.now()
    
    @app.after_request
    def after_request(response):
        """Записываем метрики после запроса"""
        if hasattr(request, 'start_time'):
            latency = (datetime.now() - request.start_time).total_seconds()
            REQUEST_LATENCY.labels(endpoint=request.endpoint or 'unknown').observe(latency)
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=request.endpoint or 'unknown',
                status=response.status_code
            ).inc()
        return response
