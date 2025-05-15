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
import time

# Função para inicializar o driver do Selenium
def init_driver():
    # Inicializa o objeto de opções para o Chrome
    chrome_options = Options()
    
    # Caminhos configurados para o Composer com a instalação do Chrome
    chrome_options.binary_location = "/usr/bin/chromium"  # Caminho para o Chrome
    chrome_options.add_argument('--headless')            # Executar o Chrome em modo headless
    chrome_options.add_argument('--no-sandbox')          # Desabilitar o sandbox (necessário no ambiente do Composer)
    chrome_options.add_argument('--disable-dev-shm-usage')  # Aumentar a memória compartilhada
    
    # Caminho para o Chromedriver (a instalação do Chromedriver no Composer normalmente estará em /usr/bin)
    service = Service('/usr/bin/chromedriver')

    # Inicializa o WebDriver com o serviço configurado e as opções definidas
    driver = webdriver.Chrome(service=service, options=chrome_options)

    return driver
# Função de scraping para extrair dados do Kabum
def extrair_dados_kabum(url):
    driver = init_driver()
    driver.get(url)
    
    # Faz o parsing do HTML com BeautifulSoup
    soup = BeautifulSoup(driver.page_source, "lxml")

    # Extrai a quantidade total de paginas
    qtd_itens = soup.find('div', id='listingCount').get_text().strip()
    index = qtd_itens.find(' ')
    qtd = qtd_itens[:index]
    ultima_pagina = math.ceil(int(qtd) / 20)


    produtos = []

    for i in range(1, ultima_pagina + 1):
        url_pag = f'{url}?page_number={i}&page_size=20&facet_filters=&sort=&variant=null'
        driver.get(url_pag)

        # Espera até que os cards estejam disponíveis na página
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "productCard"))
        )

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        produtos_pagina = soup.find_all(class_="productCard")
    # Lista para armazenar os produtos

        for produto in produtos_pagina:
            try:
                extra = produto.find("div", class_="relative flex items-start justify-between w-full p-8 pb-0 h-48")
                cupom = extra.find("div", class_="flex overflow-hidden pr-2")
                avaliacao = extra.find("span", class_="text-xxs text-black-600 leading-none pt-4")
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
                print(f"Erro ao processar produto {produto}: {e}")

    data_hoje = time.strftime("%Y-%m-%d", time.localtime())
    promocao = url.split("promocao/")[1].lower()
    
    # Configuração do bucket e upload
    bucket_name = "kabum-raw"
    file_name = f"promocao/{promocao}_produtos_{data_hoje}.csv"
    client = storage.Client()  

    bucket = client.bucket(bucket_name)
    blob = bucket.blob(file_name)

    # Criação do CSV em memória e upload para o GCS
    df = pd.DataFrame(produtos)
    with blob.open("w") as f:
        df.to_csv(f, index=False)

    driver.quit()
    return f"Arquivo {file_name} foi carregado com sucesso no bucket {bucket_name}"
