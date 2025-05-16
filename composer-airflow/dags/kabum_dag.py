"""
DAG de ETL para coletar, transformar e carregar dados da Kabum.

Este pipeline utiliza o Google Cloud Composer (Apache Airflow gerenciado) para orquestrar as etapas:
1. Extração via Web Scraping com Selenium em um contêiner Docker.
2. Transformação dos dados brutos em formato processado.
3. Carga dos dados processados em uma tabela no BigQuery.

Requisitos:
- O Docker da imagem deve conter os scripts `extraction.py` e `transformation.py`.
- As variáveis do Airflow devem estar configuradas: project_id, processed_bucket, dataset, tabela.
"""

from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
from datetime import datetime
from airflow.models import Variable
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator

# URL de origem dos dados (promoção Kabum)
url_kabum = "https://www.kabum.com.br/promocao/FESTIVALDECUPONS"

# Imagem Docker customizada com os scripts de extração e transformação
docker_image = "us-central1-docker.pkg.dev/lobobranco-458901/selenium-images/scraper:latest"  

# Variáveis do ambiente Airflow (Cloud Composer)
project_id = Variable.get("project_id")
bucket = Variable.get("processed_bucket")
dataset = Variable.get("dataset")
tabela = Variable.get("tabela")

# Definição da DAG
with DAG(
    dag_id='etl_kabum',
    default_args={
        'owner': 'lobobranco',
        'retries': 1,
    },
    description='DAG para o processamento de dados Kabum',
    schedule_interval=None,  # Execução manual
    start_date=datetime(2025, 5, 15),
    catchup=False,
) as dag:

    # Etapa 1: Extração de dados via scraping (executado no pod Kubernetes)
    extrair_dados_task = KubernetesPodOperator(
        namespace='composer-workloads',
        image=docker_image,
        cmds=["python", "/app/extraction.py"],
        arguments=[url_kabum],
        name="extrair-dados-kabum",
        task_id="extrair_dados_kabum",
        get_logs=True,
        is_delete_operator_pod=True,
    )

    # Etapa 2: Transformação dos dados (executado no mesmo contêiner)
    transformar_dados_task = KubernetesPodOperator(
        namespace='composer-workloads',
        image=docker_image,
        cmds=["python", "/app/transformation.py"],
        name="transformar-dados-kabum",
        task_id="transformar_dados_kabum",
        get_logs=True,
        is_delete_operator_pod=True,
    )

    # Etapa 3: Carga dos dados no BigQuery (usando operador nativo GCP)
    load_to_bq = GCSToBigQueryOperator(
        task_id="load_processed_data_to_bq",
        bucket=bucket,
        source_objects=["promocao/festivaldecupons_produtos_{{ ds }}.csv"],
        destination_project_dataset_table=f"{project_id}:{dataset}.{tabela}",
        source_format="CSV",
        skip_leading_rows=1,
        write_disposition="WRITE_APPEND",
        field_delimiter=",",
        autodetect=True,
    )

    # Encadeamento das tarefas
    extrair_dados_task >> transformar_dados_task >> load_to_bq
