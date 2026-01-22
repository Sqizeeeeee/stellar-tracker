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
