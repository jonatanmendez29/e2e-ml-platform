import pandas as pd
import numpy as np
import logging
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import classification_report, roc_auc_score, accuracy_score
from sklearn.model_selection import GridSearchCV
import psycopg2
import os
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
import mlflow
import mlflow.sklearn

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

class ChurnModelTrainer:
    def __init__(self, experiment_name="Customer_Churn_Predictions"):
        self.experiment_name = experiment_name
        mlflow.set_experiment(experiment_name)
        self.champion_name = None
        self.champion_model = None

    def train_models(self, X_train, X_test, y_train, y_test, feature_names):
        """Train and compare multiple models"""
        logger.info("Training multiple models...")

        models = {
            "Logistic_Regression": LogisticRegression(random_state=42, max_iter=1000),
            "Random_Forest": RandomForestClassifier(random_state=42),
            "Gradient_Boosting": GradientBoostingClassifier(random_state=42)
        }

        best_score = 0
        best_model = None
        best_model_name = ""

        for name, model in models.items():
            with mlflow.start_run(run_name=name):
                logger.info(f"Training {name}...")

                # Train model
                model.fit(X_train, y_train)

                # Make predictions
                y_pred = model.predict(X_test)
                y_pred_proba = model.predict_proba(X_test)[:, 1]

                # Calculate metrics
                accuracy = accuracy_score(y_test, y_pred)
                roc_auc = roc_auc_score(y_test, y_pred_proba)

                # Log parameters
                mlflow.log_params(model.get_params())

                # Log metrics
                mlflow.log_metrics({
                    "accuracy": accuracy,
                    "roc_auc": roc_auc
                })

                # Log model
                mlflow.sklearn.log_model(model, name)

                # Log feature importance if available
                if hasattr(model, 'feature_importances_'):
                    importance_df = pd.DataFrame({
                        'feature': feature_names,
                        'importance': model.feature_importances_
                    }).sort_values('importance', ascending=False)

                    importance_df.to_csv(f"feature_importance_{name}.csv", index=False)
                    mlflow.log_artifact(f"feature_importance_{name}.csv")

                # Log classification report
                report = classification_report(y_test, y_pred, output_dict=True)
                report_df = pd.DataFrame(report).transpose()
                report_df.to_csv(f"classification_report_{name}.csv", index=True)
                mlflow.log_artifact(f"classification_report_{name}.csv")

                # Update best model
                if roc_auc > best_score:
                    best_score = roc_auc
                    best_model = model
                    best_model_name = name

                logger.info(f"{name} - Accuracy: {accuracy:.4f}, ROC AUC: {roc_auc:.4f}")

        self.champion_name = best_model_name
        self.champion_model = best_model
        return best_model, best_model_name, best_score

    def hyperparameter_tuning(self, X_train, y_train):
        """Perform hyperparameter tuning on the best model"""
        logger.info("Performing hyperparameter tuning...")
        best_name = self.champion_name + "_Tuning"
        with mlflow.start_run(run_name=best_name):
            # Define parameter grid
            param_grid = {
                'n_estimators': [100, 200],
                'max_depth': [10, 20, None],
                'min_samples_split': [2, 5],
                'min_samples_leaf': [1, 2]
            }

            # Create model
            rf = self.champion_model

            # Grid search
            grid_search = GridSearchCV(
                rf, param_grid, cv=3, scoring='roc_auc', n_jobs=-1, verbose=1
            )

            grid_search.fit(X_train, y_train)

            # Log best parameters and score
            mlflow.log_params(grid_search.best_params_)
            mlflow.log_metric("best_cv_score", grid_search.best_score_)

            logger.info(f"Best parameters: {grid_search.best_params_}")
            logger.info(f"Best CV score: {grid_search.best_score_:.4f}")

            return grid_search.best_estimator_

    def register_best_model(self, model, model_name, run_id=None):
        """Register the best model in MLflow model registry"""
        logger.info("Registering best model...")

        if run_id:
            # Register model from a specific run
            model_uri = f"runs:/{run_id}/{model_name}"
            mv = mlflow.register_model(model_uri, "churn_prediction_model")

            # Transition to Production
            client = mlflow.tracking.MlflowClient()
            client.transition_model_version_stage(
                name="churn_prediction_model",
                version=mv.version,
                stage="production"
            )
        else:
            # Register the provided model
            mlflow.sklearn.log_model(model, "churn_prediction_model")
            # Register model
            mlflow.register_model(
                "runs:/{}/recommendation_model".format(mlflow.active_run().info.run_id),
                "churn_prediction_model"
            )

        logger.info("Model registered successfully!")

def main():
    # Initialize database connection
    db_connection = psycopg2.connect(host=os.getenv("DB_HOST", "postgres"),
        database=os.getenv("DB_NAME", "data_warehouse"),
        user=os.getenv("DB_USER", "admin_ecomm"),
        password=os.getenv("DB_PASSWORD", "admin_ecomm"),
        port=os.getenv("DB_PORT", "5432")
    )

    # Initialize feature engineer
    feature_engineer = FeatureEngineer(db_connection)

    # Load and preprocess data
    df = feature_engineer.load_data()
    df = feature_engineer.engineer_features(df)
    X_train, X_test, y_train, y_test, features = feature_engineer.preprocess_data(df)

    # Set the tracking URI to point to your MLFlow server
    mlflow.set_tracking_uri("http://mlflow:5050")

    # Initialize and run model trainer
    trainer = ChurnModelTrainer()

    # Train and compare models
    best_model, best_model_name, best_score = trainer.train_models(
        X_train, X_test, y_train, y_test, features
    )

    logger.info(f"Best model: {best_model_name} with ROC AUC: {best_score:.4f}")

    # Perform hyperparameter tuning
    tuned_model = trainer.hyperparameter_tuning(X_train, y_train)

    # Evaluate tuned model
    y_pred_proba = tuned_model.predict_proba(X_test)[:, 1]
    roc_auc = roc_auc_score(y_test, y_pred_proba)
    logger.info(f"Tuned model ROC AUC: {roc_auc:.4f}")

    # Register the best model
    trainer.register_best_model(tuned_model, "churn_prediction_model")


if __name__ == "__main__":
    main()