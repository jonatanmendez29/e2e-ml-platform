FROM jupyter/datascience-notebook:python-3.9

WORKDIR /home/jovyan/work

# Install system dependencies
USER root
RUN apt-get update && apt-get install -y \
    graphviz \
    && rm -rf /var/lib/apt/lists/*

# Switch back to jovyan user
USER jovyan

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY notebooks/ ./notebooks/
COPY scripts/ ./scripts/
COPY data/ ./data/

# Create results directory
RUN mkdir -p results

# Expose port for Jupyter
EXPOSE 8888

# Command to run Jupyter notebook
CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]