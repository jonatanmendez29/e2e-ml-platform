import pandas as pd
import mlflow
import mlflow.sklearn
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import classification_report, roc_auc_score, accuracy_score
from sklearn.model_selection import GridSearchCV
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChurnModelTrainer:
    def __init__(self, experiment_name="Customer_Churn_Prediction"):
        self.experiment_name = experiment_name
        mlflow.set_experiment(experiment_name)
        # Set the tracking URI to point to your MLFlow server
        mlflow.set_tracking_uri("http://mlflow:5050")

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

        return best_model, best_model_name, best_score

    def hyperparameter_tuning(self, X_train, y_train):
        """Perform hyperparameter tuning on the best model"""
        logger.info("Performing hyperparameter tuning...")

        with mlflow.start_run(run_name="Random_Forest_Tuning"):
            # Define parameter grid
            param_grid = {
                'n_estimators': [100, 200],
                'max_depth': [10, 20, None],
                'min_samples_split': [2, 5],
                'min_samples_leaf': [1, 2]
            }

            # Create model
            rf = RandomForestClassifier(random_state=42)

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

        logger.info("Model registered successfully!")