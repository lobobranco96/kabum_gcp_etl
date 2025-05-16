from airflow import DAG
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import KubernetesPodOperator
from datetime import datetime

url_kabum = "https://www.kabum.com.br/promocao/FESTIVALDECUPONS"
docker_image = "us-central1-docker.pkg.dev/lobobranco-458901/selenium-images/scraper:latest"  

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

    extrair_dados_task >> transformar_dados_task
