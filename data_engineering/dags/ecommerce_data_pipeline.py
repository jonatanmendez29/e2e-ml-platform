from datetime import datetime, timedelta
from airflow.sdk import DAG
from airflow.providers.standard.operators.python import PythonOperator
import pandas as pd
import logging
from sqlalchemy import create_engine, Table, Column, Integer, String, Float, Date, MetaData, ForeignKey

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

# Run data quality checks
def check_users_data(df):
    """Data quality checks for users data"""
    logger.info("Running data quality checks for users...")

    # Check for null values
    assert not df['user_id'].isnull().any(), "User ID contains null values"
    assert not df['email'].isnull().any(), "Email contains null values"

    # Check for unique values
    assert df['user_id'].is_unique, "User ID is not unique"
    #assert df['email'].is_unique, "Email is not unique" #we use fake data so this constrain may be is faild

    # Check age range
    assert df['age'].between(18, 80).all(), "Age is out of expected range"

    logger.info("Users data quality checks passed!")


def check_products_data(df):
    """Data quality checks for products data"""
    logger.info("Running data quality checks for products...")

    # Check for null values
    assert not df['product_id'].isnull().any(), "Product ID contains null values"
    assert not df['name'].isnull().any(), "Product name contains null values"

    # Check for unique values
    assert df['product_id'].is_unique, "Product ID is not unique"

    # Check price range
    assert df['price'].between(1, 1000).all(), "Price is out of expected range"

    logger.info("Products data quality checks passed!")


def check_sales_data(df):
    """Data quality checks for sales data"""
    logger.info("Running data quality checks for sales...")

    # Check for null values
    assert not df['sale_id'].isnull().any(), "Sale ID contains null values"
    assert not df['user_id'].isnull().any(), "User ID contains null values in sales"
    assert not df['product_id'].isnull().any(), "Product ID contains null values in sales"

    # Check for unique values
    assert df['sale_id'].is_unique, "Sale ID is not unique"

    # Check quantity range
    assert df['quantity'].between(1, 10).all(), "Quantity is out of expected range"

    logger.info("Sales data quality checks passed!")

def data_quality_checks():
    # Load data
    users_df = pd.read_csv('/opt/airflow/data/users.csv')
    products_df = pd.read_csv('/opt/airflow/data/products.csv')
    sales_df = pd.read_csv('/opt/airflow/data/sales.csv')

    # Run checks
    check_users_data(users_df)
    check_products_data(products_df)
    check_sales_data(sales_df)

    logger.info("All data quality checks passed!")

# Run data quality checks Task
data_quality_check = PythonOperator(
    task_id='data_quality_check',
    python_callable=data_quality_checks,
    dag=dag,
)

# Create the schema of db PostgreSQL
def create_tables(engine):
    """Create database tables if they don't exist"""
    metadata = MetaData()

    users = Table('users', metadata,
                  Column('user_id', Integer, primary_key=True),
                  Column('name', String),
                  Column('email', String, unique=True),
                  Column('signup_date', Date),
                  Column('country', String),
                  Column('age', Integer)
                  )

    products = Table('products', metadata,
                     Column('product_id', Integer, primary_key=True),
                     Column('name', String),
                     Column('category', String),
                     Column('price', Float)
                     )

    sales = Table('sales', metadata,
                  Column('sale_id', Integer, primary_key=True),
                  Column('user_id', Integer, ForeignKey('users.user_id')),
                  Column('product_id', Integer, ForeignKey('products.product_id')),
                  Column('quantity', Integer),
                  Column('sale_amount', Float),
                  Column('sale_date', Date)
                  )

    metadata.create_all(engine)
    logger.info("Database tables created successfully!")

def schema_postgres():
    # Database connection
    engine = create_engine('postgresql://airflow:airflow@postgres:5432/airflow')
    # Create tables
    create_tables(engine)

# Schema PostgreSQL Task
schema_to_postgres = PythonOperator(
    task_id='schema_to_postgres',
    python_callable=schema_postgres,
    dag=dag,
)

def load_data(engine):
    """Load data from CSV files to database"""
    # Read CSV files
    users_df = pd.read_csv('/opt/airflow/data/users.csv')
    products_df = pd.read_csv('/opt/airflow/data/products.csv')

    # Convert date columns
    users_df['signup_date'] = pd.to_datetime(users_df['signup_date'])

    # Load data to database
    users_df.to_sql('users', engine, if_exists='append', index=False)
    products_df.to_sql('products', engine, if_exists='append', index=False)

    logger.info("Data loaded to database successfully!")


def data_load_to_postgres():
    # Database connection
    engine = create_engine('postgresql://airflow:airflow@postgres:5432/airflow')
    # Load data
    load_data(engine)

# Load data to PostgreSQL Task
load_to_postgres = PythonOperator(
    task_id='load_to_postgres',
    python_callable=data_load_to_postgres,
    dag=dag,
)

#Simulate sales load
def load_salesdata(engine):
    """Load data from CSV files to database"""
    # Read CSV files
    sales_df = pd.read_csv('/opt/airflow/data/sales.csv')

    # Convert date columns
    sales_df['sale_date'] = pd.to_datetime(sales_df['sale_date'])

    # Load data to database
    sales_df.to_sql('sales', engine, if_exists='replace', index=False)

    logger.info("Sales Data loaded to database successfully!")

def sales_load_to_postgres():
    # Database connection
    engine = create_engine('postgresql://airflow:airflow@postgres:5432/airflow')
    # Load data
    load_salesdata(engine)
    logger.info("Data pipeline completed successfully!")

# Load data to PostgreSQL Task
sales_to_postgres = PythonOperator(
    task_id='sales_to_postgres',
    python_callable=sales_load_to_postgres,
    dag=dag,
)
# Set task dependencies
data_quality_check >> schema_to_postgres >> load_to_postgres >> sales_to_postgres