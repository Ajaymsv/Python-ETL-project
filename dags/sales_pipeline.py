from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
from datetime import timedelta
import os

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define DAG
with DAG(
    'sales_pipeline',
    default_args=default_args,
    description='A simple ETL pipeline for sales data',
    schedule_interval=timedelta(days=1),
    catchup=False,
    tags=['sales', 'etl'],
) as dag:

    # Task 1: Run the extraction script
    # Inside the Airflow container, directories are mapped to /opt/airflow/...
    extract_task = BashOperator(
        task_id='extract_data',
        bash_command='python3 /opt/airflow/scripts/extract.py',
        env={
            'RAW_DATA_DIR': '/opt/airflow/data/raw'
        }
    )

    # Task 2: Run the transformation script
    transform_task = BashOperator(
        task_id='transform_data',
        bash_command='python3 /opt/airflow/scripts/transform.py',
        env={
            'DUCKDB_PATH': '/opt/airflow/data/processed/sales.db',
            'RAW_DATA_DIR': '/opt/airflow/data/raw',
            'SQL_FILE_PATH': '/opt/airflow/sql/transform.sql'
        }
    )

    # Define dependencies
    extract_task >> transform_task
