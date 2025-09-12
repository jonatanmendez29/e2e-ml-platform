FROM python:3.9-slim

WORKDIR /app-ml

RUN apt-get update && apt-get install -y \
    cmake \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
COPY init_mlflow_db.py .
RUN  pip install --upgrade pip \
     && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY churn_prediction/ ./churn_prediction/
COPY recommendation/ ./recommendation/

EXPOSE 5050

CMD ["sh", "-c", "python init_mlflow_db.py && mlflow server --host 0.0.0.0 --port 5050 --backend-store-uri postgresql://admin_ecomm:admin_ecomm@postgres:5432/mlflow_tracking --default-artifact-root /mlflow/artifacts"]