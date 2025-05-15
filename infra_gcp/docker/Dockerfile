FROM us-docker.pkg.dev/airflow-helm/charts/airflow:2.9.3-python3.10

# Instalar dependências do sistema
USER root
RUN apt-get update && apt-get install -y \
    curl \
    unzip \
    gnupg \
    chromium-driver \
    chromium

# Variáveis de ambiente do Chrome
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

# Copiar e instalar dependências Python
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

USER airflow
