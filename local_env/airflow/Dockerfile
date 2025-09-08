FROM apache/airflow:3.0.6

USER root
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

USER airflow
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt