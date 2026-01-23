# =============================================================================
# StellarTracker Makefile
# =============================================================================

# Переменные
COMPOSE = docker compose
SERVICES = orchestrator orbit-service collision-service web telegram-bot
MONITORING = prometheus grafana alertmanager loki
ALL_SERVICES = $(SERVICES) $(MONITORING)

# =============================================================================
# Основные команды
# =============================================================================

.PHONY: help up down restart build logs clean

help:
	@echo "🚀 StellarTracker Makefile Commands"
	@echo ""
	@echo "📦 Основные команды:"
	@echo "  make up              - Запустить все сервисы"
	@echo "  make down            - Остановить все сервисы"
	@echo "  make restart         - Перезапустить все сервисы"
	@echo "  make build           - Собрать все образы"
	@echo "  make logs            - Показать логи всех сервисов"
	@echo "  make clean           - Остановить и удалить все (включая volumes)"
	@echo ""
	@echo "🔄 Групповые команды:"
	@echo "  make up-all          - Запустить основные сервисы + мониторинг"
	@echo "  make down-all        - Остановить основные сервисы + мониторинг"
	@echo "  make restart-all     - Перезапустить основные сервисы + мониторинг"
	@echo "  make rebuild-all     - Пересобрать основные сервисы + мониторинг"
	@echo ""
	@echo "🔄 Управление сервисами (restart-<service>):"
	@echo "  orchestrator, orbit-service, collision-service, web, telegram-bot"
	@echo ""
	@echo "🔨 Пересборка сервисов (rebuild-<service>):"
	@echo "  orchestrator, orbit-service, collision-service, web, telegram-bot"
	@echo ""
	@echo "📋 Логи сервисов (logs-<service>):"
	@echo "  orchestrator, orbit-service, collision-service, web, telegram-bot"
	@echo ""
	@echo "📊 Мониторинг:"
	@echo "  make monitoring-up         - Запустить мониторинг"
	@echo "  make monitoring-down       - Остановить мониторинг"
	@echo "  make monitoring-restart    - Перезапустить мониторинг"
	@echo "  make logs-prometheus       - Логи Prometheus"
	@echo "  make logs-grafana          - Логи Grafana"
	@echo "  make logs-alertmanager     - Логи Alertmanager"

up:
	$(COMPOSE) up -d

down:
	$(COMPOSE) down

restart:
	$(COMPOSE) restart

build:
	$(COMPOSE) build

logs:
	$(COMPOSE) logs -f

clean:
	$(COMPOSE) down -v
	@echo "🧹 Очистка завершена"

# =============================================================================
# Групповые команды для всех сервисов
# =============================================================================

.PHONY: up-all down-all restart-all rebuild-all

up-all:
	@echo "🚀 Запускаем все сервисы..."
	$(COMPOSE) up -d $(ALL_SERVICES)
	@echo "✅ Все сервисы запущены!"

down-all:
	@echo "🛑 Останавливаем все сервисы..."
	$(COMPOSE) stop $(ALL_SERVICES)
	@echo "✅ Все сервисы остановлены!"

restart-all:
	@echo "🔄 Перезапускаем все сервисы..."
	$(COMPOSE) restart $(ALL_SERVICES)
	@echo "✅ Все сервисы перезапущены!"

rebuild-all:
	@echo "🔨 Пересобираем все сервисы..."
	$(COMPOSE) build $(SERVICES)
	$(COMPOSE) up -d $(ALL_SERVICES)
	@echo "✅ Все сервисы пересобраны и запущены!"

# =============================================================================
# Управление отдельными сервисами (автогенерация)
# =============================================================================

# Генерируем команды restart-* для каждого сервиса
.PHONY: $(addprefix restart-,$(SERVICES))
$(addprefix restart-,$(SERVICES)): restart-%:
	$(COMPOSE) restart $*

# Генерируем команды rebuild-* для каждого сервиса
.PHONY: $(addprefix rebuild-,$(SERVICES))
$(addprefix rebuild-,$(SERVICES)): rebuild-%:
	$(COMPOSE) build $*
	$(COMPOSE) up -d $*

# Генерируем команды logs-* для каждого сервиса
.PHONY: $(addprefix logs-,$(SERVICES))
$(addprefix logs-,$(SERVICES)): logs-%:
	$(COMPOSE) logs -f $*

# =============================================================================
# Мониторинг
# =============================================================================

.PHONY: monitoring-up monitoring-down monitoring-restart

monitoring-up:
	$(COMPOSE) up -d $(MONITORING)

monitoring-down:
	$(COMPOSE) stop $(MONITORING)

monitoring-restart:
	$(COMPOSE) restart $(MONITORING)

# Логи мониторинга
.PHONY: $(addprefix logs-,$(MONITORING))
$(addprefix logs-,$(MONITORING)): logs-%:
	$(COMPOSE) logs -f $*

# =============================================================================
# Дополнительные команды
# =============================================================================

.PHONY: status ps

status:
	$(COMPOSE) ps

ps:
	$(COMPOSE) ps
