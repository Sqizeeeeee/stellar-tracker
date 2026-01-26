# StellarTracker — System Overview

StellarTracker is a distributed system for tracking, analyzing, and assessing the risks of orbital objects. The architecture is based on microservices, each responsible for a specific part of the workflow.

![System Overview](about/images/readme.png)

---

## Architecture Highlights

- **Microservice-based:** Each core function (data ingestion, orbit calculation, risk assessment, user interface) is implemented as a separate service.
- **gRPC Communication:** Services interact via gRPC for high performance and clear API contracts.
- **Centralized Storage:** MongoDB is used for storing users, objects, observations, and processing history.
- **Monitoring & Logging:** Prometheus, Grafana, and Loki provide observability, metrics, and alerting across all services.
- **User Interfaces:** The web dashboard is available to all users; the Telegram bot is available only to project admins.

---

## Main Components

- **Web Interface:**  
  User-facing dashboard for uploading observations, viewing tracked objects, and monitoring system health (available to all users).

- **Orchestrator:**  
  Central service that coordinates the processing pipeline: receives observations, triggers orbit calculation and risk assessment, and stores results.

- **Orbit Service:**  
  Calculates orbital elements from observations using advanced algorithms (Orekit, Batch LS, Gooding IOD).

- **Collision Service:**  
  Assesses collision risk for calculated orbits and determines risk levels.

- **Telegram Bot:**  
  Provides notifications and quick access to system status for project admins only.

- **Monitoring Stack:**  
  Prometheus collects metrics from all services, Grafana visualizes them, and Loki aggregates logs.

---

## Data Flow (Simplified)

1. **User** submits observations via Web UI or Telegram Bot.
2. **Orchestrator** receives data, calls **Orbit Service** for orbit determination.
3. **Orchestrator** then calls **Collision Service** for risk assessment.
4. Results and all data are stored in **MongoDB**.
5. **Monitoring** tools collect metrics and logs from all services.

---

## Learn More

- For details on each microservice, see their respective README files:
  - [orchestrator/README.md](orchestrator/README.md)
  - [orbit-service/README.md](orbit-service/README.md)
  - [collision-service/README.md](collision-service/README.md)
  - [web/README.md](web/README.md)
  - [telegram-bot/README.md](telegram-bot/README.md)

- For deployment and startup instructions, see [README.start.md](README.start.md).
- For monitoring and logging, see [README.monitoring.md](README.monitoring.md).

---

# StellarTracker — Обзор системы

StellarTracker — это распределённая система для отслеживания, анализа и оценки рисков орбитальных объектов. Архитектура построена на микросервисах, каждый из которых отвечает за свою часть обработки.

![Обзор системы](about/images/readme.png)

---

## Ключевые особенности архитектуры

- **Микросервисная архитектура:** Каждая основная функция (приём данных, расчёт орбиты, оценка риска, пользовательский интерфейс) реализована отдельным сервисом.
- **gRPC-взаимодействие:** Сервисы обмениваются данными через gRPC для высокой производительности и строгих API-контрактов.
- **Централизованное хранилище:** MongoDB используется для хранения пользователей, объектов, наблюдений и истории обработки.
- **Мониторинг и логирование:** Prometheus, Grafana и Loki обеспечивают наблюдаемость, сбор метрик и алерты для всех сервисов.
- **Пользовательские интерфейсы:** Веб-дэшборд доступен всем пользователям; Telegram-бот доступен только администраторам проекта.

---

## Основные компоненты

- **Веб-интерфейс:**  
  Дэшборд для загрузки наблюдений, просмотра отслеживаемых объектов и мониторинга состояния системы (доступен всем пользователям).

- **Orchestrator:**  
  Центральный сервис, координирующий обработку: принимает наблюдения, запускает расчёт орбиты и оценку риска, сохраняет результаты.

- **Orbit Service:**  
  Вычисляет орбитальные элементы по наблюдениям с помощью алгоритмов (Orekit, Batch LS, Gooding IOD).

- **Collision Service:**  
  Оценивает риск столкновения для рассчитанных орбит и определяет уровень риска.

- **Telegram-бот:**  
  Предоставляет быстрый доступ к статусу системы только администраторам проекта.

- **Мониторинговый стек:**  
  Prometheus собирает метрики со всех сервисов, Grafana визуализирует их, Loki агрегирует логи.

---

## Поток данных (упрощённо)

1. **Пользователь** отправляет наблюдения через Web UI.
2. **Orchestrator** принимает данные, вызывает **Orbit Service** для определения орбиты.
3. **Orchestrator** затем вызывает **Collision Service** для оценки риска.
4. Все результаты и данные сохраняются в **MongoDB**.
5. **Мониторинговые** инструменты собирают метрики и логи со всех сервисов.

---

## Подробнее

- Подробнее о каждом микросервисе — в их отдельных README:
  - [orchestrator/README.md](orchestrator/README.md)
  - [orbit-service/README.md](orbit-service/README.md)
  - [collision-service/README.md](collision-service/README.md)
  - [web/README.md](web/README.md)
  - [telegram-bot/README.md](telegram-bot/README.md)

- Инструкции по запуску и развёртыванию: [README.start.md](README.start.md).
- Мониторинг и логирование: [README.monitoring.md](README.monitoring.md).
