-- Create schema version table for data version control
CREATE TABLE IF NOT EXISTS schema_versions (
    version_id SERIAL PRIMARY KEY,
    version_name VARCHAR(100) NOT NULL,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);

-- Insert initial schema version
INSERT INTO schema_versions (version_name, description)
VALUES ('1.0.0', 'Initial schema for e-commerce data warehouse');

-- Create tables for e-commerce data
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    signup_date DATE,
    country VARCHAR(50),
    age INTEGER
);

CREATE TABLE IF NOT EXISTS products (
    product_id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    category VARCHAR(50),
    price DECIMAL(10, 2)
);

CREATE TABLE IF NOT EXISTS sales (
    sale_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),
    product_id INTEGER REFERENCES products(product_id),
    quantity INTEGER,
    sale_amount DECIMAL(10, 2),
    sale_date DATE
);


-- Create versioned tables for data lineage
CREATE TABLE IF NOT EXISTS users_versions (
    version_id INTEGER REFERENCES schema_versions(version_id),
    user_id INTEGER,
    name VARCHAR(100),
    email VARCHAR(100),
    signup_date DATE,
    country VARCHAR(50),
    age INTEGER,
    valid_from TIMESTAMP,
    valid_to TIMESTAMP,
    PRIMARY KEY (version_id, user_id)
);

CREATE TABLE IF NOT EXISTS products_versions (
    version_id INTEGER REFERENCES schema_versions(version_id),
    product_id INTEGER,
    name VARCHAR(100),
    category VARCHAR(50),
    price DECIMAL(10, 2),
    valid_from TIMESTAMP,
    valid_to TIMESTAMP,
    PRIMARY KEY (version_id, product_id)
);

-- Create MLflow tables (will be created automatically by MLflow)
-- Create Airflow tables (will be created automatically by Airflow)

-- Create separate databases for each service
CREATE DATABASE airflow_metadata;
CREATE DATABASE mlflow_tracking;

-- Grant permissions to our user
GRANT ALL PRIVILEGES ON DATABASE airflow_metadata TO admin_ecomm;
GRANT ALL PRIVILEGES ON DATABASE mlflow_tracking TO admin_ecomm;