#!/usr/bin/env python3
import os
import time
import psycopg2
from psycopg2 import OperationalError

def check_db_connection():
    """Check if database is available"""
    retries = 5
    delay = 2
    for i in range(retries):
        try:
            conn = psycopg2.connect(
                host="postgres",
                database="data_warehouse",
                user="admin_ecomm",
                password="admin_ecomm",
                port="5432"
            )
            conn.close()
            return True
        except OperationalError:
            if i == retries - 1:
                return False
            time.sleep(delay)
    return False

def init_mlflow_db():
    """Initialize MLFlow database"""
    if check_db_connection():
        try:
            # Run MLFlow database upgrade
            os.system("mlflow db upgrade postgresql://admin_ecomm:admin_ecomm@postgres:5432/data_warehouse")
            print("MLFlow database initialized successfully")
        except Exception as e:
            print(f"Error initializing MLFlow database: {e}")
    else:
        print("Database connection failed")

if __name__ == "__main__":
    init_mlflow_db()