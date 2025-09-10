FROM python:3.9-slim

WORKDIR /app-ml

RUN apt-get update && apt-get install -y \
    cmake \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN  pip install --upgrade pip \
     && pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["mlflow", "server", "--host", "0.0.0.0", "--port", "5000", "--backend-store-uri", "postgresql://admin_ecomm:admin_ecomm@postgres:5432/data_warehouse", "--default-artifact-root", "/mlflow/artifacts"]