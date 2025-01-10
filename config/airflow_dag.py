from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
}

with DAG(
    'crawlers_dag',
    default_args=default_args,
    description='Orchestration des crawlers',
    schedule_interval='0 0 * * *',  # Planification quotidienne
    start_date=datetime(2023, 1, 1),
    catchup=False,
) as dag:

    scrapper1_task = BashOperator(
        task_id='scrapper1',
        bash_command='python /app/scripts/scrappers/scrapper1.py'
    )

    scrapper2_task = BashOperator(
        task_id='scrapper2',
        bash_command='python /app/scripts/scrappers/scrapper2.py'
    )

    scrapper3_task = BashOperator(
        task_id='scrapper3',
        bash_command='python /app/scripts/scrappers/scrapper3.py'
    )

    scrapper1_task >> scrapper2_task >> scrapper3_task
