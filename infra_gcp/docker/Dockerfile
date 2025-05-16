FROM python:3.10-bullseye

USER root

# Instalar dependências do sistema e o Chrome/Chromedriver
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
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Variáveis de ambiente esperadas pelo Selenium
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver
ENV PATH=$PATH:/usr/bin

# Copiar requirements e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar os scripts para o diretório de trabalho
COPY extraction.py /app/extraction.py
COPY transformation.py /app/transformation.py

WORKDIR /app

# Comando padrão (pode ser sobrescrito pelo KubernetesPodOperator)
CMD ["python", "extraction.py"]
