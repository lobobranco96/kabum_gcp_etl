# 🛠️ Projeto ETL - Promoções Kabum com Selenium + Google Cloud Composer

Este projeto é uma pipeline de **Extração, Transformação e Carga (ETL)** para coletar dados da seção de promoções do site **Kabum!**, utilizando **Selenium** para Web Scraping, **BeautifulSoup** para parsing de HTML e o **Google Cloud Composer (Airflow gerenciado)** para orquestração e automação.

## 📁 Estrutura do Projeto

- `extraction.py`: Responsável por acessar a aba de promoções do site Kabum com Selenium, extrair os dados com BeautifulSoup e gerar um arquivo CSV com os produtos promocionais. O CSV é salvo na camada **Raw** do bucket no GCS.
- `transformation.py`: Realiza a limpeza e transformação dos dados brutos do CSV, aplicando regras específicas (como extração de preços, avaliações, descontos, entre outros). O resultado é um novo CSV que é salvo na camada **Processed** do bucket no GCS.

## ☁️ Infraestrutura

- **Orquestração**: [Google Cloud Composer (Airflow)](https://cloud.google.com/composer)
- **Armazenamento**: Google Cloud Storage (GCS)
  - Bucket `kabum-raw`:
    - `/promocao/`: Armazena os dados brutos extraídos da Kabum (camada Raw)
  - Bucket `kabum-processed`:
    - `/promocao/`: Armazena os dados transformados e limpos (camada Processed)

## 🧱 Banco de Dados

- **BigQuery**
  - **Dataset:** `kabum_dataset`
  - **Tabela:** `produtos`
  - Utilizado para análise e visualização dos dados com schemas definidos em JSON.

## 📦 Contêineres & Imagens

- **Artifact Registry**
  - Repositório Docker para armazenar imagens customizadas (ex: Selenium + Chrome).
  - As imagens são versionadas e utilizadas nos jobs de extração via GKE ou Composer.

## ☸️ Processamento & Execução

- **Google Kubernetes Engine (GKE)**
  - Cluster `cluster-airflow-leve` criado via Terraform.
  - Usado para execução de workloads pesadas ou paralelas relacionadas ao Airflow.
  - **Configuração:**
    - 1 nó `e2-small`
    - Disco de 10 GB
    - Integração com o Composer via permissões IAM e RBAC.

## 🔄 Fluxo do ETL

1. **Extração** (`extraction.py`):
   - Utiliza **Selenium** para simular a navegação no site da Kabum.
   - Com **BeautifulSoup**, extrai as informações dos produtos em promoção.
   - Os dados são salvos em um arquivo `.csv` e enviados para a pasta `raw/promocao/` do bucket GCS `kabum-raw`.

2. **Transformação** (`transformation.py`):
   - Os arquivos `.csv` da camada Raw são lidos diretamente do GCS.
   - As transformações aplicadas incluem:
     - Conversão de preços antigos e atuais para float.
     - Extração de percentual de desconto.
     - Extração de avaliações e unidades disponíveis.
     - Separação entre nome e detalhes do produto.
     - Padronização do campo de crédito.
   - Após transformado, o novo dataset é salvo no bucket `kabum-processed`, na pasta `/promocao/`.

3. **Carga** (BigQuery):
  - O CSV transformado é carregado diretamente do bucket kabum-processed para o BigQuery.
  - A tabela de destino é kabum_dataset.produtos.
  - O schema da tabela é definido em JSON para garantir a consistência dos dados.
  - A operação de carga pode ser realizada com o operador GCSToBigQueryOperator no Airflow.

⚙️ Tecnologias Utilizadas

```bash
Python 3.x
Selenium
BeautifulSoup
Pandas
re (expressões regulares)
Google Cloud Storage
Google Cloud Composer (Apache Airflow)
Google BigQuery
```

## Próximos passos
Incluir monitoramento e alertas via Airflow.
Carregar os dados transformados em um Data Warehouse (ex: BigQuery).


## Requisitos
Conta no Google Cloud Platform com o Composer e Storage habilitados.
Service Account com permissões adequadas.
Ambiente com dependências Python instaladas (requirements.txt).


> Projeto desenvolvido para fins educacionais e de automação de coleta de preços de produtos em promoção no e-commerce Kabum!
