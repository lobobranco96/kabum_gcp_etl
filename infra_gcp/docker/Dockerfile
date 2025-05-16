FROM apache/airflow:2.9.3-python3.10

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

# Mudar para usuário airflow para instalar dependências Python
USER airflow

COPY requirements.txt .

# Agora sim, como airflow:
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar seus scripts Python
COPY --chown=airflow:root extraction.py /app/extraction.py
COPY --chown=airflow:root transformation.py /app/transformation.py

WORKDIR /app
