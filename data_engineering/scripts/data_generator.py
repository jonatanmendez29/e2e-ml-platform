from faker import Faker
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import pathlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_users(n=1000):
    fake = Faker()
    users = []
    for i in range(n):
        name=fake.name()
        email=fake.unique.email()
        signup_date=fake.date_between(start_date='-2y', end_date='today')
        country=fake.country()
        age=np.random.randint(18, 80)
        users.append({
            "user_id": i + 1,
            "name": name,
            "email": email,
            "signup_date": signup_date,
            "country": country,
            "age": age
        })
    return pd.DataFrame(users)


def generate_products(n=100):
    fake = Faker()
    categories = ['Electronics', 'Clothing', 'Home', 'Books', 'Sports']
    products = []
    for i in range(n):
        products.append({
            "product_id": i + 1,
            "name": fake.word().capitalize() + ' ' + fake.word(),
            "category": np.random.choice(categories),
            "price": round(np.random.uniform(5, 500), 2)
        })
    return pd.DataFrame(products)


def generate_sales(users_df, products_df, n=10000):
    sales = []
    start_date = datetime.now() - timedelta(days=365)
    for i in range(n):
        user = users_df.sample(1).iloc[0]
        product = products_df.sample(1).iloc[0]
        sale_date = start_date + timedelta(days=np.random.randint(0, 365))
        sales.append({
            "sale_id": i + 1,
            "user_id": user['user_id'],
            "product_id": product['product_id'],
            "quantity": np.random.randint(1, 5),
            "sale_amount": round(product['price'] * np.random.randint(1, 5), 2),
            "sale_date": sale_date.strftime('%Y-%m-%d')
        })
    return pd.DataFrame(sales)

def main():
    logger.info("Generating users data...")
    users_df = generate_users(n=1000)

    logger.info("Generating products data...")
    products_df = generate_products(n=50)

    logger.info("Generating sales data...")
    sales_df = generate_sales(users_df, products_df, n=5000)

    # Ensure directory exists
    pathlib.Path('../data').mkdir(parents=True, exist_ok=True)

    # Save to CSV
    users_df.to_csv('../data/users.csv', index=False)
    products_df.to_csv('../data/products.csv', index=False)
    sales_df.to_csv('../data/sales.csv', index=False)

    logger.info("Data generation completed!")

if __name__ == "__main__":
    main()