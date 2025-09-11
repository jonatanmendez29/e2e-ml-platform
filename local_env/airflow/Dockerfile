FROM apache/airflow:3.0.6

USER root
RUN apt-get update && apt-get install -y \
    cmake \
    gcc \
    build-essential \
    libpq-dev \
    graphviz \
    && rm -rf /var/lib/apt/lists/*

USER airflow
COPY requirements.txt .
COPY airflow/scripts/ ./scripts/
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && mkdir -p data \
    && python3 scripts/data_generator.py