import sys
import os
import asyncio

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

EXTRACT_DIR = "/opt/airflow"
if EXTRACT_DIR not in sys.path:
    sys.path.append(EXTRACT_DIR)

from src.services.s3.minio_service import BucketOperations
from src.services.arxiv_manager import ArxivScrapingManager
from src.services.open_ai.translater import OpenAITranslater

minio = BucketOperations(
    os.environ['MINIO_URL'],
    os.environ['MINIO_ACCESS_KEY'],
    os.environ['MINIO_SECRET_KEY']
)

BUCKET_RAW_NAME = 'raw'
BUCKET_TRANSLATED_NAME = 'translated'


def get_papers_from_arxiv():
    manager = ArxivScrapingManager(minio, BUCKET_RAW_NAME)
    asyncio.run(manager.run_arxiv_papers(batch_size=5, delay=3))


def translate_pdf_file(**kwargs):
    file_name = kwargs.get("dag_run").conf.get("file_name")
    if not file_name:
        raise ValueError("File_name not provided in DAG run config.")
    translator = OpenAITranslater(minio, BUCKET_RAW_NAME, file_name, language="ukrainian")
    translated_text = translator.translate_pdf_file().encode('utf-8')
    date_today = datetime.now().strftime("%Y-%m-%d")
    minio.write_content_to_file(BUCKET_TRANSLATED_NAME, file_name.replace("pdf", "txt"),
                                translated_text, folder_path=f'{date_today}/',
                                content_type='application/txt')


with DAG(
    dag_id="arxiv_scraping_and_translation",
    start_date=datetime(2025, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=["arxiv", "scraping"],
) as dag:

    scrape_task = PythonOperator(
        task_id="scrape_arxiv_papers",
        python_callable=get_papers_from_arxiv,
        provide_context=True,
    )


with DAG(
    dag_id="arxiv_translation_pdf_file",
    start_date=datetime(2025, 1, 1),
    schedule_interval=None,
    catchup=False,
    tags=["arxiv", "translation"],
) as dag:

    translate_task = PythonOperator(
        task_id="translate_pdf_file",
        python_callable=translate_pdf_file,
        provide_context=True,
    )


