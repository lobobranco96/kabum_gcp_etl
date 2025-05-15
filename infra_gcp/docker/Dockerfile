FROM us-docker.pkg.dev/airflow-helm/charts/airflow:2.9.3-python3.10

USER root

# Instalar Chrome e Chromedriver com compatibilidade entre versões
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    gnupg \
    fonts-liberation \
    libnss3 \
    libxss1 \
    libasound2 \
    libx11-xcb1 \
    chromium \
    chromium-driver \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Definir variáveis de ambiente
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver
ENV PATH=$PATH:/usr/bin

# Copiar dependências Python
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copiar seus scripts Python para dentro do container
COPY extraction.py /app/extraction.py
COPY transformation.py /app/transformation.py

WORKDIR /app

USER airflow
