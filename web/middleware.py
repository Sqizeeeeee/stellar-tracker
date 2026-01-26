"""
Middleware для StellarTracker
"""
from flask import request
from prometheus_client import Counter, Histogram
from datetime import datetime

# Prometheus метрики
REQUEST_COUNT = Counter('web_requests_total', 'Total web requests', ['method', 'endpoint', 'status'])
REQUEST_LATENCY = Histogram('web_request_duration_seconds', 'Request latency', ['endpoint'])


HTTP_REQUESTS_TOTAL = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status', 'service']
)

HTTP_REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration',
    ['method', 'endpoint', 'service'],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10)
)


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
            endpoint = request.endpoint or 'unknown'

            REQUEST_LATENCY.labels(endpoint=endpoint).observe(latency)
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=endpoint,
                status=response.status_code
            ).inc()

            HTTP_REQUESTS_TOTAL.labels(
                method=request.method,
                endpoint=endpoint,
                status=response.status_code,
                service='web-service'
            ).inc()

            HTTP_REQUEST_DURATION.labels(
                method=request.method,
                endpoint=endpoint,
                service='web-service'
            ).observe(latency)

        return response
