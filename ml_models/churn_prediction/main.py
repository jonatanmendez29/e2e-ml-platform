from sqlalchemy import create_engine
import logging
from sklearn.metrics import roc_auc_score

from feature_engineering import FeatureEngineer
from train import ChurnModelTrainer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    # Initialize database connection
    db_connection = create_engine('postgresql://airflow:airflow@localhost:5432/airflow')

    # Initialize feature engineer
    feature_engineer = FeatureEngineer(db_connection)

    # Load and preprocess data
    df = feature_engineer.load_data()
    df = feature_engineer.engineer_features(df)
    X_train, X_test, y_train, y_test, features = feature_engineer.preprocess_data(df)

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