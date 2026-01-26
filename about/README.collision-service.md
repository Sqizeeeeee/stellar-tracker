# Обзор сервиса Collision Service StellarTracker

Collision Service — это микросервис для оценки риска столкновения орбитальных объектов с Землёй. Он принимает орбитальные элементы, рассчитывает ключевые параметры (например, MOID) и определяет уровень риска для объекта.



---

## Основные функции

- **Оценка риска столкновения:**  
  Принимает орбитальные элементы объекта и вычисляет вероятность опасного сближения с Землёй.
- **Расчёт MOID и перигелия:**  
  Определяет минимальное расстояние между орбитой объекта и орбитой Земли (MOID), а также перигелий.
- **Классификация риска:**  
  Присваивает уровень риска (high, moderate, low) и флаг потенциальной опасности.
- **Экспорт метрик:**  
  Отправляет бизнес-метрики и технические показатели в Prometheus для мониторинга.
- **Логирование:**  
  Ведёт журнал событий и ошибок для диагностики.

---

## Архитектура и взаимодействие

- **gRPC API:**  
  Реализует gRPC-сервер для приёма запросов на оценку риска от Orchestrator.
- **Prometheus:**  
  Экспортирует метрики (количество оценок, ошибки, время обработки и др.).
- **Docker:**  
  Развёртывается в отдельном контейнере, поддерживает переменные окружения для настройки.

---

## Основные модули и файлы

- `collision-service/server.py` — основной gRPC-сервер, логика оценки риска.
- `collision-service/requirements.txt` — зависимости Python.
- `collision-service/Dockerfile` — контейнеризация сервиса.
- `collision-service/proto/` — gRPC-протоколы и сгенерированные файлы.
- `collision-service/` — дополнительные утилиты и вспомогательные модули.

---

## Взаимодействие с другими сервисами

- **Orchestrator:**  
  Получает запросы на оценку риска, возвращает рассчитанные параметры и уровень риска.
- **Prometheus/Grafana:**  
  Метрики доступны для мониторинга и визуализации.

---

## Безопасность и доступ

- **Валидация данных:**  
  Проверяет корректность входных орбитальных элементов перед расчётом.
- **Изоляция:**  
  Сервис работает в отдельном контейнере и не хранит пользовательские данные.

---

## Пример пользовательских сценариев

**Оценка риска по орбитальным элементам:**  
Orchestrator отправляет орбитальные элементы объекта, Collision Service рассчитывает MOID, перигелий, определяет уровень риска и возвращает результат для отображения пользователю.

---

## Дополнительная информация

- Подробности по запуску и настройке — в [README.start.md](README.start.md)
- Описание архитектуры всей системы — в [README.systemoverview.md](README.systemoverview.md)
- Мониторинг и метрики — в [README.monitoring.md](README.monitoring.md)

---

# StellarTracker Collision Service Overview

Collision Service is a microservice for assessing the collision risk of orbital objects with Earth. It accepts orbital elements, calculates key parameters (such as MOID), and determines the risk level for the object.


---

## Main Features

- **Collision Risk Assessment:**  
  Accepts an object's orbital elements and computes the probability of a hazardous approach to Earth.
- **MOID and Perihelion Calculation:**  
  Determines the Minimum Orbit Intersection Distance (MOID) between the object's orbit and Earth's, as well as the perihelion.
- **Risk Classification:**  
  Assigns a risk level (high, moderate, low) and a potential hazard flag.
- **Metrics Export:**  
  Sends business and technical metrics to Prometheus for monitoring.
- **Logging:**  
  Maintains an event and error log for diagnostics.

---

## Architecture and Interactions

- **gRPC API:**  
  Implements a gRPC server to receive risk assessment requests from the Orchestrator.
- **Prometheus:**  
  Exports metrics (assessment count, errors, processing time, etc.).
- **Docker:**  
  Deployed as a separate container, supports environment variables for configuration.

---

## Main Modules and Files

- `collision-service/server.py` — main gRPC server, risk assessment logic.
- `collision-service/requirements.txt` — Python dependencies.
- `collision-service/Dockerfile` — service containerization.
- `collision-service/proto/` — gRPC protocols and generated files.
- `collision-service/` — additional utilities and helper modules.

---

## Integration with Other Services

- **Orchestrator:**  
  Receives risk assessment requests, returns calculated parameters and risk level.
- **Prometheus/Grafana:**  
  Metrics are available for monitoring and visualization.

---

## Security and Access

- **Data Validation:**  
  Checks the correctness of input orbital elements before calculation.
- **Isolation:**  
  The service runs in a separate container and does not store user data.

---

## Example User Scenario

**Risk Assessment from Orbital Elements:**  
The Orchestrator sends an object's orbital elements, Collision Service calculates MOID, perihelion, determines the risk level, and returns the result for user display.

---

## Additional Information

- For details on launch and configuration, see [README.start.md](README.start.md)
- For overall system architecture, see [README.systemoverview.md](README.systemoverview.md)
- For monitoring and metrics, see [README.monitoring.md](README.monitoring.md)
