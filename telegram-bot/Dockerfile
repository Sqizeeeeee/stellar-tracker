FROM python:3.11-slim

WORKDIR /app

# Копируем requirements из telegram-bot папки
COPY telegram-bot/requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код бота из telegram-bot папки
COPY telegram-bot/ .

# Expose webhook port
EXPOSE 8080

# Запускаем бота
CMD ["python", "bot.py"]
