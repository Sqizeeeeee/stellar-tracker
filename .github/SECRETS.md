# GitHub Secrets Configuration

Перейдите в: `Settings` → `Secrets and variables` → `Actions` → `New repository secret`

## Required Secrets

### Deployment Secrets
- `SSH_PRIVATE_KEY` - SSH ключ для доступа к серверу
- `SERVER_HOST` - Хост сервера (например: `stellartracker.example.com`)
- `SERVER_USER` - Пользователь для SSH (например: `deploy`)
- `DEPLOY_PATH` - Путь на сервере (например: `/opt/stellartracker`)

### Application Secrets
- `SECRET_KEY` - Flask secret key (64 символа)
- `MONGO_INITDB_ROOT_PASSWORD` - Пароль MongoDB root
- `GRAFANA_PASSWORD` - Пароль Grafana admin

### Optional
- `SLACK_WEBHOOK` - Webhook для уведомлений в Slack (опционально)

## Environments

Создайте environments: `Settings` → `Environments`

### Staging
- `MONGODB_URI` = `mongodb://admin:password@mongodb:27017/stellartracker?authSource=admin`

### Production  
- `MONGODB_URI` = `mongodb://admin:password@mongodb:27017/stellartracker?authSource=admin`

## Генерация ключей

```bash
# SECRET_KEY
openssl rand -hex 32

# SSH ключ
ssh-keygen -t ed25519 -C "github-actions@stellartracker"
# Приватный ключ → SSH_PRIVATE_KEY
# Публичный ключ → добавить на сервер ~/.ssh/authorized_keys
```
