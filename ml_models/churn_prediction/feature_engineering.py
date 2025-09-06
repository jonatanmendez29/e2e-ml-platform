import pandas as pd
import numpy as np
import logging
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FeatureEngineer:
    def __init__(self, db_connection):
        self.db_conn = db_connection
        self.scaler = StandardScaler()
        self.label_encoder = LabelEncoder()

    def load_data(self):
        """Load data from PostgreSQL database"""
        logger.info("Loading data from database...")

        # Query to get user features and churn status
        query = """
        WITH user_metrics AS (
            SELECT 
                u.user_id,
                u.country,
                u.age,
                COUNT(s.sale_id) AS total_orders,
                SUM(s.sale_amount) AS total_spent,
                MIN(s.sale_date) AS first_order_date,
                MAX(s.sale_date) AS last_order_date,
                EXTRACT(DAY FROM NOW() - MAX(s.sale_date)) AS days_since_last_order,
                AVG(s.sale_amount) AS avg_order_value
            FROM users u
            LEFT JOIN sales s ON u.user_id = s.user_id
            GROUP BY u.user_id, u.country, u.age
        ),
        churn_status AS (
            SELECT 
                user_id,
                CASE 
                    WHEN EXTRACT(DAY FROM NOW() - MAX(sale_date)) > 90 THEN 1 
                    ELSE 0 
                END AS churned
            FROM sales
            GROUP BY user_id
        )
        SELECT 
            um.*,
            COALESCE(cs.churned, 1) AS churned  -- If no sales, consider as churned
        FROM user_metrics um
        LEFT JOIN churn_status cs ON um.user_id = cs.user_id
        """

        df = pd.read_sql_query(query, self.db_conn)
        return df

    def engineer_features(self, df):
        """Create additional features for the model"""
        logger.info("Engineering features...")

        # Create time-based features
        df['customer_duration_days'] = (df['last_order_date'] - df['first_order_date']).dt.days
        df['order_frequency'] = df['total_orders'] / df['customer_duration_days'].replace(0, 1)

        # Create monetary-based features
        df['daily_spend'] = df['total_spent'] / df['customer_duration_days'].replace(0, 1)

        # Handle infinite values
        df = df.replace([np.inf, -np.inf], 0)

        # Fill NaN values
        df = df.fillna(0)

        return df

    def preprocess_data(self, df):
        """Preprocess data for modeling"""
        logger.info("Preprocessing data...")

        # Encode categorical variables
        df['country_encoded'] = self.label_encoder.fit_transform(df['country'])

        # Select features for modeling
        features = [
            'age', 'total_orders', 'total_spent', 'days_since_last_order',
            'avg_order_value', 'customer_duration_days', 'order_frequency',
            'daily_spend', 'country_encoded'
        ]

        X = df[features]
        y = df['churned']

        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        # Scale numerical features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)

        return X_train_scaled, X_test_scaled, y_train, y_test, features

    def get_feature_names(self):
        """Get feature names after preprocessing"""
        return self.scaler.get_feature_names_out()