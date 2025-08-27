import pandas as pd
from sqlalchemy import create_engine, Table, Column, Integer, String, Float, Date, MetaData, ForeignKey
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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


def load_data(engine):
    """Load data from CSV files to database"""
    # Read CSV files
    users_df = pd.read_csv('/opt/airflow/data/users.csv')
    products_df = pd.read_csv('/opt/airflow/data/products.csv')
    sales_df = pd.read_csv('/opt/airflow/data/sales.csv')

    # Convert date columns
    users_df['signup_date'] = pd.to_datetime(users_df['signup_date'])
    sales_df['sale_date'] = pd.to_datetime(sales_df['sale_date'])

    # Load data to database
    users_df.to_sql('users', engine, if_exists='replace', index=False)
    products_df.to_sql('products', engine, if_exists='replace', index=False)
    sales_df.to_sql('sales', engine, if_exists='replace', index=False)

    logger.info("Data loaded to database successfully!")


def main():
    # Database connection
    engine = create_engine('postgresql://admin:admin@postgres:5432/data_warehouse')

    # Create tables
    create_tables(engine)

    # Load data
    load_data(engine)

    logger.info("Data pipeline completed successfully!")


if __name__ == "__main__":
    main()