FROM python:3.10-slim

# Instala pacotes necessários do sistema
RUN apt-get update && apt-get install -y \
    wget curl unzip gnupg2 \
    fonts-liberation libappindicator3-1 libasound2 libatk-bridge2.0-0 \
    libnspr4 libnss3 libxss1 lsb-release xdg-utils \
    chromium chromium-driver \
    && apt-get clean

# Define paths esperados pelo selenium
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

# Cria diretório de trabalho
WORKDIR /app

# Copia os arquivos do projeto
COPY . .

# Instala bibliotecas Python necessárias
RUN pip install --no-cache-dir -r requirements.txt

# Comando de execução
CMD ["python", "extractation.py"]
