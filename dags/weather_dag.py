import textwrap

from datetime import timedelta, datetime
from airflow.models.dag import DAG
from airflow.operators.python import PythonOperator

from get_raw_data import run_daily_weather_pipeline

with DAG(
    "weather",
    default_args = {
        "depends_on_past": False,
        "retries": 1,
        "retry_delay": timedelta(minutes=1)
        # 'queue': 'bash_queue',
        # 'pool': 'backfill',
        # 'priority_weight': 10,
        # 'end_date': datetime(2016, 1, 1),
        # 'wait_for_downstream': False,
        # 'execution_timeout': timedelta(seconds=300),
        # 'on_failure_callback': some_function, # or list of functions
        # 'on_success_callback': some_other_function, # or list of functions
        # 'on_retry_callback': another_function, # or list of functions
        # 'sla_miss_callback': yet_another_function, # or list of functions
        # 'on_skipped_callback': another_function, #or list of functions
        # 'trigger_rule': 'all_success'
    },
    description="Simple weather data ETL dag",
    schedule=timedelta(days=1),
    start_date=datetime(2025, 12, 11),
    catchup=False,
    tags=["example"],    
) as dag:
    # Runs the ETL pipeline
    run_batch_process = PythonOperator(
        task_id="load_weather_data",
        python_callable=run_daily_weather_pipeline
    )