.PHONY: help up down logs restart clean build

help:
	@echo "StellarTracker Commands"
	@echo "======================="
	@echo "up          - Start all services"
	@echo "monitoring  - Start with monitoring"
	@echo "down        - Stop all services"
	@echo "logs        - View logs"
	@echo "web-logs    - View web logs only"
	@echo "restart     - Restart services"
	@echo "build       - Rebuild images"
	@echo "clean       - Clean containers & images (keep volumes)"
	@echo "clean-all   - Clean EVERYTHING including volumes"
	@echo "rebuild     - Full rebuild (keep volumes)"
	@echo "status      - Show services status"
	@echo "health      - Check services health"

up:
	docker-compose up -d

monitoring:
	docker-compose --profile monitoring up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

web-logs:
	docker-compose logs -f web

restart:
	docker-compose restart

build:
	docker-compose build

clean:
	@echo "🧹 Cleaning everything (keeping volumes)..."
	docker-compose down --rmi all
	@echo "✅ Done!"

clean-all:
	@echo "🧹 Cleaning EVERYTHING including volumes..."
	docker-compose down -v --rmi all
	@echo "✅ Done!"

rebuild:
	@echo "🔄 Full rebuild from scratch (keeping volumes)..."
	@make clean
	@make build
	@make up
	@echo "✅ Rebuild complete!"

restart-web:
	@echo "🔄 Restarting web service (using volume mount - no rebuild needed)..."
	docker-compose restart web
	@echo "✅ Web service restarted!"

rebuild-web:
	@echo "🔄 Full rebuild of web service..."
	docker-compose stop web
	docker-compose build web
	docker-compose up -d web
	@echo "✅ Web service fully rebuilt!"

restart-orchestrator:
	@echo "🔄 Restarting orchestrator service..."
	docker-compose restart orchestrator
	@echo "✅ Orchestrator service restarted!"

rebuild-orchestrator:
	@echo "🔄 Full rebuild of orchestrator service..."
	docker-compose stop orchestrator
	docker-compose build orchestrator
	docker-compose up -d orchestrator
	@echo "✅ Orchestrator service fully rebuilt!"

status:
	@echo "📊 Services Status:"
	@docker-compose ps

health:
	@echo "🏥 Health Check:"
	@curl -s http://localhost:5001/api/health | python -m json.tool || echo "Web service not responding"
	@echo ""

debug:
	@echo "🔍 Debugging Information:"
	@echo "\n📦 Container Status:"
	@docker-compose ps
	@echo "\n📊 Last 50 lines of web logs:"
	@docker-compose logs --tail=50 web
	@echo "\n🌐 Network ports:"
	@docker ps --format "table {{.Names}}\t{{.Ports}}"

shell:
	@echo "🐚 Opening shell in web container..."
	docker-compose exec web /bin/sh || docker-compose exec web /bin/bash

test-connection:
	@echo "🔌 Testing connections..."
	@echo "Web service root:"
	@curl -v http://localhost:5001/ 2>&1 | head -20
	@echo "\n\nAPI health endpoint:"
	@curl -s http://localhost:5001/api/health 2>&1
	@echo "\n\nChecking if port 5001 is listening:"
	@lsof -i :5001 || echo "Port 5001 not in use"

test-endpoints:
	@echo "🧪 Testing all endpoints..."
	@echo "\n1️⃣ Root (/):"
	@curl -s -o /dev/null -w "Status: %{http_code}\n" http://localhost:5001/
	@echo "\n2️⃣ Health (/api/health):"
	@curl -s -o /dev/null -w "Status: %{http_code}\n" http://localhost:5001/api/health
	@echo "\n3️⃣ Metrics (/metrics):"
	@curl -s -o /dev/null -w "Status: %{http_code}\n" http://localhost:5001/metrics
	@echo "\n4️⃣ Login (/login):"
	@curl -s -o /dev/null -w "Status: %{http_code}\n" http://localhost:5001/login

proto-gen:
	@echo "🔧 Regenerating proto files..."
	@echo "→ Orchestrator (C++)..."
	protoc --proto_path=proto --cpp_out=orchestrator/src --grpc_out=orchestrator/src --plugin=protoc-gen-grpc=`which grpc_cpp_plugin` proto/astro.proto
	@echo "→ Web (Python)..."
	python -m grpc_tools.protoc -I./proto --python_out=./web/proto --grpc_python_out=./web/proto ./proto/astro.proto
	@echo "✅ Proto files regenerated!"

test:
	@echo "🧪 Running tests..."
	@docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit
	@docker-compose -f docker-compose.test.yml down
