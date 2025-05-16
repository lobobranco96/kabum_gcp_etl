from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
from datetime import datetime
from airflow.models import Variable
from airflow.providers.google.cloud.transfers.gcs_to_bigquery import GCSToBigQueryOperator
from airflow.utils.dates import days_ago

url_kabum = "https://www.kabum.com.br/promocao/FESTIVALDECUPONS"
docker_image = "us-central1-docker.pkg.dev/lobobranco-458901/selenium-images/scraper:latest"  

project_id = Variable.get("project_id")
bucket = Variable.get("processed_bucket")
dataset = Variable.get("dataset")
tabela = Variable.get("tabela")

# project_id = "lobobranco-458901"
# bucket = "kabum-processed"
# dataset = "kabum_dataset"
# tabela = "produtos"
with DAG(
    'etl_kabum',
    default_args={
        'owner': 'lobobranco',
        'retries': 1,
    },
    description='DAG para o processamento de dados Kabum',
    schedule_interval=None,
    start_date=datetime(2025, 5, 15),
    catchup=False,
) as dag:

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

    transformar_dados_task = KubernetesPodOperator(
        namespace='composer-workloads',
        image=docker_image,
        cmds=["python", "/app/transformation.py"],
        name="transformar-dados-kabum",
        task_id="transformar_dados_kabum",
        get_logs=True,
        is_delete_operator_pod=True,
    )

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
    extrair_dados_task >> transformar_dados_task >> load_to_bq
