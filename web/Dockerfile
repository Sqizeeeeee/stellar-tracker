FROM python:3.11-slim as base

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements from web directory
COPY web/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code from web directory
COPY web/ .

# Expose port
EXPOSE 5000

# Production stage
FROM base as production
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "app:app"]

# Test stage
FROM base as test
RUN pip install pytest pytest-cov pytest-asyncio
CMD ["pytest", "tests/", "-v", "--cov=.", "--cov-report=xml"]
