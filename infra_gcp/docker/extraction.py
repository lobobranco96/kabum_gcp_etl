from google.cloud import storage

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup
import time
import pandas as pd
import math
import sys
import logging

# Configuração do logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def init_driver():
    chrome_options = Options()
    chrome_options.binary_location = "/usr/bin/chromium"
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    service = Service('/usr/bin/chromedriver')
    return webdriver.Chrome(service=service, options=chrome_options)

def extrair_dados_kabum(url):
    driver = init_driver()
    logging.info(f"Acessando a URL: {url}")
    driver.get(url)

    soup = BeautifulSoup(driver.page_source, "lxml")
    qtd_itens = soup.find('div', id='listingCount').get_text().strip()
    qtd = int(qtd_itens.split(' ')[0])
    ultima_pagina = math.ceil(qtd / 20)
    logging.info(f"Total de itens: {qtd} - Total de páginas: {ultima_pagina}")

    produtos = []

    for i in range(1, ultima_pagina + 1):
        url_pag = f'{url}?page_number={i}&page_size=20&facet_filters=&sort=&variant=null'
        logging.info(f"Scraping da página {i}: {url_pag}")
        driver.get(url_pag)

        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "productCard"))
            )
        except Exception as e:
            logging.warning(f"Timeout esperando produtos na página {i}: {e}")
            continue

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        produtos_pagina = soup.find_all(class_="productCard")

        for produto in produtos_pagina:
            try:
                extra = produto.find("div", class_="relative flex items-start justify-between w-full p-8 pb-0 h-48")
                cupom = extra.find("div", class_="flex overflow-hidden pr-2") if extra else None
                avaliacao = extra.find("span", class_="text-xxs text-black-600 leading-none pt-4") if extra else None
                nome = produto.find("span", class_="nameCard")
                preco_antigo = produto.find("span", class_="oldPriceCard")
                preco_atual = produto.find("span", class_="priceCard")
                credito = produto.find(class_="text-xs text-black-600 desktop:leading-4")
                desconto = produto.find("div", class_="text-xs flex rounded-8 text-white-500 px-4 h-16 group-hover:hidden desktop:mt-4 desktopLarge:mt-2 bg-secondary-500")
                link = "https://www.kabum.com.br" + produto.find("a", class_="productLink")["href"]
                unidades = produto.find("span", class_="text-xxs font-semibold text-black-800 group-hover:hidden")

                produtos.append({
                    "nome_produto": nome.text if nome else "",
                    "preco_antigo": preco_antigo.get_text(strip=True) if preco_antigo else "", 
                    "preco_atual": preco_atual.get_text(strip=True) if preco_atual else "" ,
                    "credito": credito.get_text(strip=True) if credito else "" ,
                    "desconto": desconto.get_text(strip=True) if desconto else "" ,
                    "avaliacao": avaliacao.get_text(strip=True) if avaliacao else "" ,
                    "cupom": cupom.get_text(strip=True) if cupom else "", 
                    "link": link,
                    "unidades": unidades.get_text(strip=True) if unidades else ""
                })
            except Exception as e:
                logging.error(f"Erro ao processar produto: {e}")

    driver.quit()

    data_hoje = time.strftime("%Y-%m-%d", time.localtime())
    promocao = url.split("promocao/")[1].lower()

    bucket_name = "kabum-raw"
    file_name = f"promocao/{promocao}_produtos_{data_hoje}.csv"
    
    df = pd.DataFrame(produtos)

    try:
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(file_name)

        with blob.open("w") as f:
            df.to_csv(f, index=False)

        logging.info(f"Arquivo salvo com sucesso em: gs://{bucket_name}/{file_name}")
        return f"Arquivo {file_name} foi carregado com sucesso no bucket {bucket_name}"

    except Exception as e:
        logging.error(f"Erro ao salvar arquivo no bucket: {e}")
        raise

def main():
    url = sys.argv[1]
    resultado = extrair_dados_kabum(url)
    logging.info(resultado)

if __name__ == "__main__":
    main()
