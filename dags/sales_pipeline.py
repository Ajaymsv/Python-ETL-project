from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from airflow.utils.task_group import TaskGroup
from airflow.utils.dates import days_ago
from datetime import timedelta

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
    description='A production-ready ETL pipeline for sales data',
    schedule_interval=timedelta(days=1),
    catchup=False,
    tags=['sales', 'etl', 'production'],
) as dag:

    # Start and End Markers
    start_pipeline = EmptyOperator(task_id='start_pipeline')
    end_pipeline = EmptyOperator(task_id='end_pipeline')

    # Task Group for Ingestion
    with TaskGroup(group_id='ingestion_layer', tooltip='Extracts mock e-commerce data') as ingestion_layer:

        extract_data = BashOperator(
            task_id='extract_data',
            bash_command='python3 /opt/airflow/scripts/extract.py',
            env={
                'RAW_DATA_DIR': '/opt/airflow/data/raw'
            },
            append_env=True
        )

    # Task Group for Transformation and Validation
    with TaskGroup(group_id='transformation_layer', tooltip='Validates data and calculates business metrics') as transformation_layer:

        transform_data = BashOperator(
            task_id='transform_data',
            bash_command='python3 /opt/airflow/scripts/transform.py',
            env={
                'DUCKDB_PATH': '/opt/airflow/data/processed/sales.db',
                'RAW_DATA_DIR': '/opt/airflow/data/raw',
                'SQL_FILE_PATH': '/opt/airflow/sql/transform.sql'
            },
            append_env=True
        )

    # Define dependencies
    start_pipeline >> ingestion_layer >> transformation_layer >> end_pipeline
