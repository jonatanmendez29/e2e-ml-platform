FROM jupyter/scipy-notebook:latest

WORKDIR /home/jovyan/work
# Install additional system dependencies if needed
USER root
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    gcc \
    graphviz \
    && rm -rf /var/lib/apt/lists/*

# Copy custom configuration files
COPY jupyter_server_config.py /home/jovyan/.jupyter/
COPY jupyter_config.py /home/jovyan/.jupyter/jupyter_notebook_config.py
# Set correct ownership
RUN chown -R jovyan:users /home/jovyan/.jupyter
# Switch back to jovyan user
USER jovyan
# Install specific Python packages that aren't included in the base image
# Use conda for problematic packages
RUN conda install -c conda-forge osqp

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

CMD ["jupyter", "notebook", "--config=/home/jovyan/.jupyter/jupyter_notebook_config.py"]