<details open>
<summary><strong>English</strong></summary>

# StellarTracker

## Quick Start

### 1. Clone repository
```bash
git clone https://github.com/yourusername/stellartracker.git
cd stellartracker
```

### 2. Setup environment
```bash
# Скопировать пример конфигурации
cp .env.example .env

# Сгенерировать SECRET_KEY
openssl rand -hex 32

# Отредактировать .env и заменить пароли
nano .env
```

### 3. Run locally
```bash
make up
```

## CI/CD Setup

См. [.github/SECRETS.md](.github/SECRETS.md) для настройки GitHub Secrets.

## Development

```bash
make help  # Показать все команды
```

</details>

<details>
<summary><strong>Русский</strong></summary>

# StellarTracker

## Быстрый старт

### 1. Клонировать репозиторий
```bash
git clone https://github.com/yourusername/stellartracker.git
cd stellartracker
```

### 2. Настроить окружение
```bash
# Скопировать пример конфигурации
cp .env.example .env

# Сгенерировать SECRET_KEY
openssl rand -hex 32

# Отредактировать .env и заменить пароли
nano .env
```

### 3. Запустить локально
```bash
make up
```

## Настройка CI/CD

См. [.github/SECRETS.md](.github/SECRETS.md) для настройки GitHub Secrets.

## Разработка

```bash
make help  # Показать все команды
```

</details>
