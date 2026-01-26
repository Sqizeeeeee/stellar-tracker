# 📊 StellarTracker Monitoring Setup

## Обзор

Стек мониторинга включает:
- **Prometheus** - сбор метрик
- **Grafana** - визуализация данных
- **Loki** - агрегация логов
- **Promtail** - сбор логов
- **Node Exporter** - системные метрики
- **cAdvisor** - метрики контейнеров

## Быстрый старт

### 1. Запуск только приложения (без мониторинга)

```bash
# Запустить основные сервисы
docker compose up -d

# Проверить статус
docker compose ps
```

### 2. Запуск с мониторингом

```bash
# Запустить все сервисы включая мониторинг
docker compose --profile monitoring up -d

# Или явно указать профили
docker compose --profile monitoring up -d

# Проверить все запущенные сервисы
docker compose --profile monitoring ps
```

### 3. Остановка сервисов

```bash
# Остановить только основные сервисы
docker compose down

# Остановить все включая мониторинг
docker compose --profile monitoring down

# Остановить и удалить volumes
docker compose --profile monitoring down -v
```

### 4. Доступ к интерфейсам

- **Grafana**: http://localhost:3000
  - Логин: `admin`
  - Пароль: `stellartracker_admin` (или из переменной `GRAFANA_PASSWORD`)
  
- **Prometheus**: http://localhost:9090
- **Loki**: http://localhost:3100
- **cAdvisor**: http://localhost:8080

## Структура файлов

```
monitoring/
├── prometheus/
│   ├── prometheus.yml      # Основная конфигурация
│   └── rules/
│       └── alerts.yml      # Правила алертинга
├── promtail/
│   └── promtail.yml        # Конфигурация сбора логов
└── grafana/
    ├── datasources.yml     # Источники данных
    └── dashboards.yml      # Конфигурация дашбордов
```

## Метрики

### Стандартные метрики приложений:
- `http_requests_total` - количество HTTP запросов
- `http_request_duration_seconds` - время обработки запросов
- `process_cpu_seconds_total` - использование CPU
- `process_resident_memory_bytes` - использование памяти

### Метрики collision-service:
- `collision_detection_duration_seconds` - время детекции столкновений
- `collision_checks_total` - количество проверок столкновений
- `satellites_tracked` - количество отслеживаемых спутников

## Алерты

Настроены следующие алерты:
- **HighCPUUsage** - CPU выше 80% более 5 минут
- **HighMemoryUsage** - память выше 1GB
- **ServiceDown** - сервис недоступен более 1 минуты
- **HighErrorRate** - частота ошибок выше 5%
- **SlowAPIResponse** - 95-й перцентиль времени ответа выше 1с

## Рекомендуемые дашборды Grafana

Импортируйте следующие дашборды по ID:
- **1860** - Node Exporter Full
- **893** - Docker and System Monitoring
- **7362** - PostgreSQL Database
- **13639** - Loki & Promtail

## Troubleshooting

### Prometheus не видит таргеты
```bash
# Проверьте конфигурацию
docker compose -f docker-compose.monitoring.yml exec prometheus promtool check config /etc/prometheus/prometheus.yml

# Проверьте логи
docker compose -f docker-compose.monitoring.yml logs prometheus
```

### Promtail не собирает логи
```bash
# Проверьте права доступа к Docker socket
docker compose -f docker-compose.monitoring.yml logs promtail
```

### Grafana не показывает данные
```bash
# Проверьте подключение к Prometheus
curl http://localhost:9090/api/v1/query?query=up

# Проверьте datasources в Grafana
curl -u admin:stellartracker_admin http://localhost:3000/api/datasources
```

## Масштабирование

Для production окружения:
1. Настройте retention для Prometheus (по умолчанию 15 дней)
2. Используйте внешнее хранилище для Grafana дашбордов
3. Настройте Alertmanager для отправки уведомлений
4. Используйте remote storage для долгосрочного хранения метрик

## Безопасность

⚠️ **Важно**: Измените дефолтные пароли перед production deployment!

```yaml
# В docker-compose.monitoring.yml
environment:
  - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
```

## Переменные окружения

Создайте файл `.env` для настройки:

```env
# Grafana
GRAFANA_PASSWORD=your_secure_password

# Другие настройки
COLLISION_SERVICE_URL=http://collision-service:8001
```

## Команды для разработки

```bash
# Запустить только основное приложение
docker compose up -d backend collision-service

# Запустить только мониторинг
docker compose --profile monitoring up -d prometheus grafana loki

# Перезапустить конкретный сервис
docker compose restart prometheus

# Посмотреть логи мониторинга
docker compose --profile monitoring logs -f prometheus grafana

# Обновить конфигурацию Prometheus без перезапуска
docker compose exec prometheus wget --post-data="" http://localhost:9090/-/reload
```
