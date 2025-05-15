from airflow import DAG
from airflow.operators.python import PythonOperator
from extraction import extrair_dados_kabum
from transformation import transformacao_kabum
from datetime import datetime

url_kabum = "https://www.kabum.com.br/promocao/festivaldecupons"

with DAG(
    'processamento_kabum',
    default_args={
        'owner': 'airflow',
        'retries': 3,
    },
    description='DAG para o processamento de dados Kabum',
    schedule_interval=None,  # ou um cronograma fixo, por exemplo, '0 12 * * *'
    start_date=datetime(2025, 5, 14),
    catchup=False,
) as dag:

    # Tarefa de extração de dados
    extrair_dados_task = PythonOperator(
        task_id='extrair_dados_kabum',
        python_callable=extrair_dados_kabum,
        op_args=[url_kabum],  # Passando a URL como parâmetro para a função
    )

    # Tarefa de transformação dos dados
    transformar_dados_task = PythonOperator(
        task_id='transformar_dados_kabum',
        python_callable=transformacao_kabum,
    )

    # Definindo a sequência de execução das tarefas
    extrair_dados_task >> transformar_dados_task
