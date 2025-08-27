import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_users_data(df):
    """Data quality checks for users data"""
    logger.info("Running data quality checks for users...")

    # Check for null values
    assert not df['user_id'].isnull().any(), "User ID contains null values"
    assert not df['email'].isnull().any(), "Email contains null values"

    # Check for unique values
    assert df['user_id'].is_unique, "User ID is not unique"
    assert df['email'].is_unique, "Email is not unique"

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


def main():
    # Load data
    users_df = pd.read_csv('/opt/airflow/data/users.csv')
    products_df = pd.read_csv('/opt/airflow/data/products.csv')
    sales_df = pd.read_csv('/opt/airflow/data/sales.csv')

    # Run checks
    check_users_data(users_df)
    check_products_data(products_df)
    check_sales_data(sales_df)

    logger.info("All data quality checks passed!")


if __name__ == "__main__":
    main()