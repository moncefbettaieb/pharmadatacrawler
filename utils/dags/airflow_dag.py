from airflow import DAG
from airflow.models import Variable
from airflow.providers.docker.operators.docker import DockerOperator
from datetime import datetime

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 1,
}

project_id = 'fournisseur-data'
APP_ENV = 'dev'

with DAG(
    'crawlers_dag',
    default_args=default_args,
    description='Orchestration des crawlers',
    schedule_interval='0 0 * * *',  # Planification quotidienne
    start_date=datetime(2023, 1, 1),
    catchup=False,
) as dag:

    scrapper1_task = DockerOperator(
        task_id='save_sitemaps_links_to_mongo',
        image='europe-west9-docker.pkg.dev/${project_id}/cloud-run-source-deploy/scrappers:latest',
        container_name='save_sitemaps_links_to_mongo-container',
        api_version='auto',
        auto_remove='force',
        command='scripts/scrappers/save_sitemaps_links_to_mongo.py',
        environment={
            'APP_ENV': 'uat'
        },
        docker_url='unix://var/run/docker.sock',
        network_mode='bridge',
    )

    scrapper2_task = DockerOperator(
        task_id='pharma_gdd_scraper',
        image='europe-west9-docker.pkg.dev/${project_id}/cloud-run-source-deploy/scrappers:latest',
        container_name='pharma_gdd_scraper-container',
        api_version='auto',
        auto_remove='force',
        command='scripts/scrappers/pharma_gdd_scraper.py',
        environment={
            'APP_ENV': 'uat'
        },
        docker_url='unix://var/run/docker.sock',
        network_mode='bridge',
    )

    scrapper1_task >> scrapper2_task
