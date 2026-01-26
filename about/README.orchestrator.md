# Обзор сервиса Orchestrator StellarTracker

Orchestrator — это центральный микросервис, координирующий обработку наблюдений в системе StellarTracker. Он принимает данные от веб-сервиса, управляет вызовами сервисов расчёта орбиты и оценки риска, а также сохраняет результаты в базу данных.

---

## Основные функции

- **Приём наблюдений:**  
  Получает данные наблюдений от веб-интерфейса или других источников.

- **Оркестрация пайплайна:**  
  Запускает последовательную обработку: расчёт орбиты (Orbit Service) и оценка риска (Collision Service).

- **Агрегация и возврат результатов:**  
  Собирает результаты обработки и возвращает их пользователю через веб-сервис.

- **Логирование и метрики:**  
  Ведёт журнал событий, экспортирует бизнес-метрики для мониторинга.

---

## Архитектура и взаимодействие

- **gRPC API:**  
  Orchestrator реализует gRPC-сервер для приёма и обработки запросов от веб-сервиса.

- **Вызовы внешних сервисов:**  
  Для расчёта орбиты и оценки риска использует gRPC-клиентов для обращения к Orbit Service и Collision Service.

- **MongoDB:**  
  Сохраняет результаты обработки, объекты и историю в централизованное хранилище.

- **Prometheus:**  
  Экспортирует метрики (количество обработанных запросов, ошибки, время обработки и др.).

- **Docker:**  
  Развёртывается в отдельном контейнере, поддерживает переменные окружения для настройки адресов сервисов и БД.

---

## Основные модули и файлы

- `orchestrator/server.py` — основной gRPC-сервер, логика обработки запросов, интеграция с внешними сервисами.
- `orchestrator/requirements.txt` — зависимости Python.
- `orchestrator/Dockerfile` — контейнеризация сервиса.
- `orchestrator/proto/` — gRPC-протоколы и сгенерированные файлы.
- `orchestrator/` — дополнительные утилиты и вспомогательные модули.

---

## Взаимодействие с другими сервисами

- **Web Service:**  
  Получает наблюдения, инициирует обработку, возвращает результаты пользователю.

- **Orbit Service:**  
  Вызывает для расчёта орбитальных элементов по наблюдениям.

- **Collision Service:**  
  Вызывает для оценки риска столкновения по рассчитанным орбитам.

- **MongoDB:**  
  Сохраняет объекты, результаты и историю обработки.

- **Prometheus/Grafana:**  
  Метрики доступны для мониторинга и визуализации.

---

## Безопасность и доступ

- **Аутентификация:**  
  Обычно вызывается только доверенными сервисами внутри инфраструктуры.
- **Валидация данных:**  
  Проверяет корректность входных данных перед обработкой.

---

## Пример сценария обработки

**Обработка новых наблюдений:**  
Orchestrator получает пакет наблюдений, вызывает Orbit Service для расчёта орбиты, затем Collision Service для оценки риска, сохраняет результаты в MongoDB и возвращает их веб-сервису для отображения пользователю.

---

## Дополнительная информация

- Подробности по запуску и настройке — в [README.start.md](../README.start.md)
- Описание архитектуры всей системы — в [README.systemoverview.md](../about/README.systemoverview.md)
- Мониторинг и метрики — в [README.monitoring.md](../README.monitoring.md)

---

# StellarTracker Orchestrator Service Overview

The Orchestrator is the central microservice that coordinates the processing of observations in the StellarTracker system. It receives data from the web service, manages calls to the orbit calculation and risk assessment services, and stores results in the database.

---

## Main Features

- **Receiving Observations:**  
  Accepts observation data from the web interface or other sources.

- **Pipeline Orchestration:**  
  Runs sequential processing: orbit calculation (Orbit Service) and risk assessment (Collision Service).

- **Result Aggregation and Response:**  
  Collects processing results and returns them to the user via the web service.

- **Logging and Metrics:**  
  Maintains an event log and exports business metrics for monitoring.

---

## Architecture and Interactions

- **gRPC API:**  
  Orchestrator implements a gRPC server to receive and process requests from the web service.

- **External Service Calls:**  
  Uses gRPC clients to call Orbit Service and Collision Service for orbit calculation and risk assessment.

- **MongoDB:**  
  Stores processing results, objects, and history in centralized storage.

- **Prometheus:**  
  Exports metrics (number of processed requests, errors, processing time, etc.).

- **Docker:**  
  Deployed as a separate container, supports environment variables for configuring service and DB addresses.

---

## Main Modules and Files

- `orchestrator/server.py` — main gRPC server, request processing logic, integration with external services.
- `orchestrator/requirements.txt` — Python dependencies.
- `orchestrator/Dockerfile` — service containerization.
- `orchestrator/proto/` — gRPC protocols and generated files.
- `orchestrator/` — additional utilities and helper modules.

---

## Integration with Other Services

- **Web Service:**  
  Receives observations, initiates processing, returns results to the user.

- **Orbit Service:**  
  Called for calculating orbital elements from observations.

- **Collision Service:**  
  Called for assessing collision risk based on calculated orbits.

- **MongoDB:**  
  Stores objects, results, and processing history.

- **Prometheus/Grafana:**  
  Metrics are available for monitoring and visualization.

---

## Security and Access

- **Authentication:**  
  Typically called only by trusted services within the infrastructure.
- **Data Validation:**  
  Checks the correctness of input data before processing.

---

## Example Processing Scenario

**Processing New Observations:**  
The Orchestrator receives a batch of observations, calls the Orbit Service for orbit calculation, then the Collision Service for risk assessment, saves the results to MongoDB, and returns them to the web service for user display.

---

## Additional Information

- For details on launch and configuration, see [README.start.md](../README.start.md)
- For overall system architecture, see [README.systemoverview.](README.systemoverview.md)
- For monitoring and metrics, see [README.monitoring.md](../README.monitoring.md)
