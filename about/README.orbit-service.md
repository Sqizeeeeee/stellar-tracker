# Обзор сервиса Orbit Service StellarTracker

Orbit Service — это специализированный микросервис для вычисления орбитальных элементов по наблюдениям. Он реализован с использованием Python и библиотеки Orekit (через JPype), что обеспечивает высокую точность и поддержку современных астродинамических алгоритмов.

![Orbit Service Interface](images/orbit_service.png)

---

## Основные функции

- **Расчёт орбиты:**  
  Принимает на вход серию наблюдений (время, RA, Dec) и вычисляет орбитальные элементы объекта.
- **Поддержка нескольких алгоритмов:**  
  Использует Batch Least Squares, Gooding IOD и упрощённые методы для разных сценариев и количества наблюдений.
- **Экспорт метрик:**  
  Отправляет бизнес-метрики и технические показатели в Prometheus для мониторинга.
- **Логирование:**  
  Ведёт журнал событий и ошибок для диагностики.

---

## Архитектура и взаимодействие

- **gRPC API:**  
  Реализует gRPC-сервер для приёма запросов на расчёт орбиты от Orchestrator.
- **Orekit (через JPype):**  
  Использует Java-библиотеку Orekit для точных астродинамических вычислений.
- **Prometheus:**  
  Экспортирует метрики (количество расчётов, ошибки, время обработки и др.).
- **Docker:**  
  Развёртывается в отдельном контейнере, поддерживает переменные окружения для настройки путей к данным Orekit и JVM.

---

## Основные модули и файлы

- `orbit-service/orbit_service.py` — основной gRPC-сервер, логика расчёта орбит, интеграция с Orekit.
- `orbit-service/requirements.txt` — зависимости Python.
- `orbit-service/Dockerfile` — контейнеризация сервиса.
- `orbit-service/proto/` — gRPC-протоколы и сгенерированные файлы.
- `orbit-service/` — дополнительные утилиты и вспомогательные модули.

---

## Взаимодействие с другими сервисами

- **Orchestrator:**  
  Получает запросы на расчёт орбиты, возвращает вычисленные элементы.
- **Prometheus/Grafana:**  
  Метрики доступны для мониторинга и визуализации.

---

## Безопасность и доступ

- **Валидация данных:**  
  Проверяет корректность входных наблюдений перед расчётом.
- **Изоляция:**  
  Сервис работает в отдельном контейнере и не хранит пользовательские данные.

---

## Пример пользовательских сценариев

**Расчёт орбиты по наблюдениям:**  
Orchestrator отправляет три и более наблюдений, Orbit Service вычисляет орбитальные элементы (a, e, i, ω, Ω, M, epoch) и возвращает результат для дальнейшей оценки риска.

---

## Дополнительная информация

- Подробности по запуску и настройке — в [README.start.md](../README.start.md)
- Описание архитектуры всей системы — в [README.systemoverview.md](../about/README.systemoverview.md)
- Мониторинг и метрики — в [README.monitoring.md](../README.monitoring.md)

---

# StellarTracker Orbit Service Overview

Orbit Service is a specialized microservice for calculating orbital elements from observations. It is implemented in Python using the Orekit library (via JPype), providing high accuracy and support for modern astrodynamics algorithms.

![Orbit Service Interface](images/orbit_service.png)

---

## Main Features

- **Orbit Calculation:**  
  Accepts a series of observations (time, RA, Dec) and computes the object's orbital elements.
- **Multiple Algorithms Supported:**  
  Uses Batch Least Squares, Gooding IOD, and simplified methods for different scenarios and observation counts.
- **Metrics Export:**  
  Sends business and technical metrics to Prometheus for monitoring.
- **Logging:**  
  Maintains an event and error log for diagnostics.

---

## Architecture and Interactions

- **gRPC API:**  
  Implements a gRPC server to receive orbit calculation requests from the Orchestrator.
- **Orekit (via JPype):**  
  Uses the Java Orekit library for precise astrodynamics computations.
- **Prometheus:**  
  Exports metrics (calculation count, errors, processing time, etc.).
- **Docker:**  
  Deployed as a separate container, supports environment variables for configuring Orekit data paths and JVM.

---

## Main Modules and Files

- `orbit-service/orbit_service.py` — main gRPC server, orbit calculation logic, Orekit integration.
- `orbit-service/requirements.txt` — Python dependencies.
- `orbit-service/Dockerfile` — service containerization.
- `orbit-service/proto/` — gRPC protocols and generated files.
- `orbit-service/` — additional utilities and helper modules.

---

## Integration with Other Services

- **Orchestrator:**  
  Receives orbit calculation requests and returns computed elements.
- **Prometheus/Grafana:**  
  Metrics are available for monitoring and visualization.

---

## Security and Access

- **Data Validation:**  
  Checks the correctness of input observations before calculation.
- **Isolation:**  
  The service runs in a separate container and does not store user data.

---

## Example User Scenario

**Orbit Calculation from Observations:**  
The Orchestrator sends three or more observations, Orbit Service computes the orbital elements (a, e, i, ω, Ω, M, epoch), and returns the result for further risk assessment.

---

## Additional Information

- For details on launch and configuration, see [README.start.md](../README.start.md)
- For overall system architecture, see [README.systemoverview.md](../about/README.systemoverview.md)
- For monitoring and metrics, see [README.monitoring.md](../README.monitoring.md)
