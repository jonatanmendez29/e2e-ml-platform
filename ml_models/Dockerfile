FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY churn_prediction/requirements.txt .
COPY recommendation/requirements.txt .
RUN pip install --no-cache-dir -r churn_prediction/requirements.txt -r recommendation/requirements.txt

# Copy application code
COPY common/ /app/common/
COPY churn_prediction/ /app/churn_prediction/
COPY recommendation/ /app/recommendation/

# Create directory for MLflow
RUN mkdir -p /mlflow

# Expose MLflow UI port
EXPOSE 5000

# Command to run MLflow server
CMD ["mlflow", "server", "--host", "0.0.0.0", "--port", "5000", "--backend-store-uri", "sqlite:///mlflow/mlflow.db", "--default-artifact-root", "/mlflow/artifacts"]