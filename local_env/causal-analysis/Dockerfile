FROM jupyter/datascience-notebook:python-3.9

USER root
RUN apt-get update && apt-get install -y \
    graphviz \
    && rm -rf /var/lib/apt/lists/*

USER jovyan

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8888

CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]