from datetime import datetime, timedelta

import airflow
from airflow.sdk import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.providers.standard.operators.bash import BashOperator

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    dag_id='ingest_data_pipeline',
    default_args=default_args,
    description='An end-to-end ecommerce data pipeline',
    schedule=None,
    catchup=False,
)

# Generate data
generate_data = PythonOperator(
    task_id='generate_data',
    python_callable=lambda: exec(open('/opt/airflow/scripts/data_generator.py').read()),
    dag=dag,
)

# Run data quality checks
data_quality_check = PythonOperator(
    task_id='data_quality_check',
    python_callable=lambda: exec(open('/opt/airflow/scripts/data_quality_checks.py').read()),
    dag=dag,
)

# Load data to PostgreSQL
load_to_postgres = PythonOperator(
    task_id='load_to_postgres',
    python_callable=lambda: exec(open('/opt/airflow/scripts/load_to_postgres.py').read()),
    dag=dag,
)

# Set task dependencies
generate_data >> data_quality_check >> load_to_postgres