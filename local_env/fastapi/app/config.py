import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # API settings
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", "8000"))
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"

    # Database settings
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "airflow")
    DB_USER = os.getenv("DB_USER", "airflow")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "airflow")
    DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

    # MLflow settings
    MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")

    # Model names
    CHURN_MODEL_NAME = os.getenv("CHURN_MODEL_NAME", "churn_prediction_model")
    RECOMMENDATION_MODEL_NAME = os.getenv("RECOMMENDATION_MODEL_NAME", "product_recommendation_model")


settings = Settings()