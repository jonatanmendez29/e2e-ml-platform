FROM jupyter/datascience-notebook:python-3.9

WORKDIR /home/jovyan/work
# Install additional system dependencies if needed
USER root
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    graphviz \
    && rm -rf /var/lib/apt/lists/*
# Switch back to jovyan user
USER jovyan
# Install specific Python packages that aren't included in the base image
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY notebooks/ ./notebooks/
COPY scripts/ ./scripts/
COPY data/ ./data/
# Create results directory
RUN mkdir -p results

EXPOSE 8888

CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]