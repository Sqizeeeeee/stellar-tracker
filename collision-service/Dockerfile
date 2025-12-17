FROM python:3.11-slim
WORKDIR /app

COPY web/proto ./web/proto
COPY collision-service/server.py server.py

RUN pip install --no-cache-dir grpcio grpcio-tools prometheus-client
CMD ["python", "server.py"]